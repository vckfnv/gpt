import torch
from torch.utils.data import DataLoader # 데이터로더
from gluonnlp.data import SentencepieceTokenizer 
from kogpt2.utils import get_tokenizer
from kogpt2.utils import download, tokenizer
from kogpt2.model.torch_gpt2 import GPT2Config, GPT2LMHeadModel
from kogpt2.data import Read_Dataset
import gluonnlp
from kogpt2.model.sample import sample_sequence
from tqdm import tqdm
import subprocess
from tensorboardX import SummaryWriter
import re

def main(input_sent, load_path = './checkpoint/KoGPT2_checkpoint_qt1_samsung40_1000.tar'):
        
    #finetuning 불러오기

    pytorch_kogpt2 = {
        'url':
        'https://kobert.blob.core.windows.net/models/kogpt2/pytorch/pytorch_kogpt2_676e9bcfa7.params',
        'fname': 'pytorch_kogpt2_676e9bcfa7.params',
        'chksum': '676e9bcfa7'
    }


    kogpt2_config = {
        "initializer_range": 0.02,
        "layer_norm_epsilon": 1e-05,
        "n_ctx": 1024,
        "n_embd": 768,
        "n_head": 12,
        "n_layer": 12,
        "n_positions": 1024,
        "vocab_size": 50000
    }

    ctx = 'cpu'
    cachedir = '~/kogpt2/'
    #save_path = 'checkpoint/'


    #학습된 결과를 불러오는 경로
    # load_path = './checkpoint/KoGPT2_checkpoint_qt1_samsung0_1000.tar'

    # download model
    model_info = pytorch_kogpt2
    model_path = download(model_info['url'],
                model_info['fname'],
                model_info['chksum'],
                cachedir=cachedir)
    # download vocab
    vocab_info = tokenizer
    vocab_path = download(vocab_info['url'],
                vocab_info['fname'],
                vocab_info['chksum'],
                cachedir=cachedir)

    # Device 설정
    device = torch.device(ctx)
    # 저장한 Checkpoint 불러오기
    checkpoint = torch.load(load_path, map_location=device)

    # KoGPT-2 언어 모델 학습을 위한 GPT2LMHeadModel 선언
    kogpt2model = GPT2LMHeadModel(config=GPT2Config.from_dict(kogpt2_config))
    kogpt2model.load_state_dict(checkpoint['model_state_dict'])

    kogpt2model.eval()
    vocab_b_obj = gluonnlp.vocab.BERTVocab.from_sentencepiece(vocab_path,
                                mask_token=None,
                                sep_token=None,
                                cls_token=None,
                                unknown_token='<unk>',
                                padding_token='<pad>',
                                bos_token='<s>',
                                eos_token='</s>')

    tok_path = get_tokenizer()
    model, vocab = kogpt2model, vocab_b_obj
    tok = SentencepieceTokenizer(tok_path)

    sent = sample_sequence(model.to("cpu"), tok, vocab, sent=input_sent, text_size=110, temperature=0.5, top_p=0.8, top_k=40)
    sent = sent.replace("<unused0>", "\n")

    return sent