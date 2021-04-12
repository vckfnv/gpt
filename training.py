#!/usr/bin/env python
# coding: utf-8

# In[1]:


from google.colab import drive
drive.mount('/content/drive')


# In[2]:


import os
os.chdir("/content/drive/My Drive/KoGPT2")
os.getcwd()


# In[6]:


get_ipython().system('pip install -r requirements.txt')
get_ipython().system('pip install .')


# In[4]:


get_ipython().system('pip install torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html')


# In[ ]:


get_ipython().system('nvidia-smi')


# In[1]:


import torch
torch.__version__


# In[ ]:


import torch
torch.cuda.get_device_name(0)


# In[3]:


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


# In[76]:


#모델 다운로드

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

def get_gpu_memory_map():
	"""Get the current gpu usage.
	Returns
	-------
	usage: dict
		Keys are device ids as integers.
		Values are memory usage as integers in MB.
	"""
	result = subprocess.check_output(
		[
			'nvidia-smi', '--query-gpu=memory.used',
			'--format=csv,nounits,noheader'
		], encoding='utf-8')
	# Convert lines into a dictionary
	gpu_memory = [int(x) for x in result.strip().split('\n')]
	gpu_memory_map = dict(zip(range(len(gpu_memory)), gpu_memory))
	return gpu_memory_map


ctx = 'cuda' #'cuda' #'cpu' #학습 Device CPU or GPU. colab의 경우 GPU 사용
cachedir = '~/kogpt2/' # KoGPT-2 모델 다운로드 경로
use_cuda = True # Colab내 GPU 사용을 위한 값

#시각화를 위한 툴
#summary = SummaryWriter()

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

# KoGPT-2 언어 모델 학습을 위한 GPT2LMHeadModel 선언
kogpt2model = GPT2LMHeadModel(config=GPT2Config.from_dict(kogpt2_config))

# model_path 로부터 다운로드 받은 내용을 load_state_dict 으로 업로드
kogpt2model.load_state_dict(torch.load(model_path))

device = torch.device(ctx)
kogpt2model.to(device)


# In[16]:


##초기화 상태에서 문장생성

kogpt2model.eval()

vocab_b_obj = gluonnlp.vocab.BERTVocab.from_sentencepiece(vocab_path,
                                                          mask_token=None,
                                                          sep_token = None,
                                                          cls_token = None,
                                                          unknown_token='<unk>',
                                                          padding_token='<pad>',
                                                          bos_token='<s>',
                                                          eos_token='</s>')
tok_path = get_tokenizer()
model, vocab = kogpt2model, vocab_b_obj
sentencepieceTokenizer = SentencepieceTokenizer(tok_path)

tok = SentencepieceTokenizer(tok_path)

sent = sample_sequence(model.to("cpu"), tok, vocab, sent="삼성전자는 2020년", text_size=100, temperature=0.7, top_p=0.8, top_k=40)
sent = sent.replace("<unused0>", "\n")
print(sent)


# In[80]:


#학습범위 조절
epoch = 3

#학습결과를 저장하는 경로
save_path = 'checkpoint/'

#생성 결과를 저장할 경로
samples = "samples/"

#학습할 데이터를 불러오는 경로
data_file_path = 'dataset/'
data_name = 'qt1_hyundaimotor.txt'

#배치사이즈
batch_size = 8



#keyword_en = ["new_product", "stock", "invest", "sales", "recruit", "hr", "culture", "salary"]
#company = 'samsung'
#data_file_name = []

#for keyword in keyword_en:
  #data_file_name.append(f'{company}_{keyword}.txt')


# In[81]:


# 학습하기

kogpt2model.train()

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

dataset = Read_Dataset(data_file_path+data_name, vocab, tok)
data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, pin_memory=True)

learning_rate = 3e-5
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

print('KoGPT-2 Transfer Learning Start')
avg_loss = (0.0, 0.0)

count = 0
for epoch in range(epoch):
  for data in data_loader:
    optimizer.zero_grad()
    data = torch.stack(data) # list of Tensor로 구성되어 있기 때문에 list를 stack을 통해 변환해준다.
    data = data.transpose(1,0)
    data = data.to(ctx)
    model = model.to(ctx)

    outputs = model(data, labels=data)
    loss, logits = outputs[:2]
    loss = loss.to(ctx)
    loss.backward()
    avg_loss = (avg_loss[0] * 0.99 + loss, avg_loss[1] * 0.99 + 1.0)
    optimizer.step()

    if count % 100 == 0:
      print('epoch no.{0} train no.{1}  loss = {2:.5f} avg_loss = {3:.5f}' . format(epoch, count, loss, avg_loss[0] / avg_loss[1]))

    count += 1

  if (epoch > 0 and epoch % 5 == 0):

    # generator 진행
    sent = sample_sequence(model.to("cpu"), tok, vocab, sent="삼성전자 신제품은", text_size=100, temperature=0.7, top_p=0.8, top_k=40)
    sent = sent.replace("<unused0>", "\n")
    print(sent)

    #txt파일저장
    f = open(samples + data_name[:-4] + '.txt', 'a', encoding="utf-8")
    f.write('epoch no.{0} train no.{1}  loss = {2:.5f} avg_loss = {3:.5f}'.format(epoch, count, loss, avg_loss[0] / avg_loss[1]))
    f.write('\n')
    f.write(sent)
    f.write('\n\n')
    f.close
    #########################################

  if (epoch > 0 and epoch % 20 == 0):
    # 모델 저장
    try:
      torch.save({
        'epoch': epoch,
        'train_no': count,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss
      }, save_path + 'KoGPT2_checkpoint_' + data_name[:-4] + '_' +str(epoch) + '_' + str(count) + '.tar')
    except:
      pass


# In[ ]:


sent = sample_sequence(model.to("cpu"), tok, vocab, sent="삼성 신제품", text_size=100, temperature=0.7, top_p=0.8, top_k=40)
sent = sent.replace("<unused0>", "\n")
print(sent)


# In[ ]:


#시각화를 위한 툴
tensorboard --logdir=runs


# In[ ]:




