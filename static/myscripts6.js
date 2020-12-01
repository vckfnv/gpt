var typingBool = true;
$('.generated2').hide();

//카드 마우스오버시 그림자
$(document).ready(function() {
    // executes when HTML-Document is loaded and DOM is ready
   console.log("document is ready");
     
   
     $( ".card" ).hover(
     function() {
       $(this).addClass('shadow-lg').css('cursor', 'pointer'); 
     }, function() {
       $(this).removeClass('shadow-lg');
     }
   );
     
   // document ready  
   });
   
   $(document).ready(function(){
    $('.loader').hide();
  })

//문장 생성
$('.generate').on('click', function() {
  $('.generated2').text('');
  $('.generated3').text('');
  $('.loader').show();
  $.ajax({
    url:"/gptprocess",
    type:'POST',
    dataType:'json',
    contentType:'application/json',
    data: JSON.stringify({ 
      'gensent' : $('.gensent').val(),
      'quarter' : $('.qt').text(),
      'com_id' : $('.hidden_com_id2').attr('value')
    }),
    context: this,
    success:function(data){
      $('.loader').hide();
      console.log(data.gen);
      $('.generated2').text(data.gen);
      var typingBool = false;
      var typingIdx=0; 
      var typingTxt = $(".generated2").text(); // 타이핑될 텍스트를 가져온다 
      typingTxt=typingTxt.split(""); // 한글자씩 자른다. 
      if(typingBool==false){ // 타이핑이 진행되지 않았다면 
          typingBool=true; 
          
          var tyInt = setInterval(typing,50); // 반복동작 
        } 
        
        function typing(){ 
          if(typingIdx<typingTxt.length){ // 타이핑될 텍스트 길이만큼 반복 
            $(".generated3").append(typingTxt[typingIdx]); // 한글자씩 이어준다. 
            typingIdx++; 
          } else{ 
            clearInterval(tyInt); //끝나면 반복종료 
          } 
        }
    },
    error: function(err){
      $('.loader').hide();
      $('.generated3').text("죄송합니다. 아직 해당 시기의 기업 자료가 없습니다. 빠른 시일 내에 추가하겠습니다.");
    }
  }); 
})

//분기 바뀜
$('.qtbtn').on('click',function(){
  colorchange = true;
  $('.qtbtn').css({
    "background-color" : "#fafafa",
    "color" : "#6c757c"
  });
  $('.qt').text($(this).attr('value'));
  $(this).css({
    "background-color" : "#6c757c",
    "color" : "white"});
})

//카테고리 바뀜
$('.catebtn').on('click', function() {
  $('.article').text('');
  $('.article2').text('');
  $('.catebtn').css({
    "background-color" : "#fafafa",
    "color" : "#6c757c"
  });
  $('.category').text($(this).attr('value'));
  $(this).css({
    "background-color" : "#6c757c",
    "color" : "white"});
  $.ajax({
    url:"/issueprocess",
    type:'POST',
    dataType:'json',
    contentType:'application/json',
    data: JSON.stringify({ 
      'quarter' : $('.qt').text(),
      'com_id' : $('.hidden_com_id2').attr('value'),
      'category_id' : $('.category').text()
    }),
    context: this,
    success:function(data){
      console.log(data);
      $('.test').attr('src',Flask.url_for('static', {filename : 'images/graph/'+data[0][9]}));
      $('.test2').attr('src',Flask.url_for('static', {filename : 'images/graph/'+data[0][10]}));
      $('#issueul').html('');
      data.forEach(element => {
        console.log(element[0])
        var plusli = document.createElement('li');
        plusli.style.cssText = 'margin:5px;display:block;';
        var plusa = document.createElement('a');
        plusa.setAttribute('href',"javascript:void(0)");
        plusa.setAttribute('value',element[8]);
        plusa.style.cssText = "color : rgb(80, 79, 79)";
        plusa.innerHTML = '<span style="font-size:small;font-weight: lighter;color: rgb(184, 182, 182);">ISSUE '+(Number(element[7])+1)+'</span><br>'+element[0]+'<br>';
        plusa.classList.add("issue");

        plusa.onclick = function(){
          console.log('clicked');
          $('.article').text('');
          $('.article2').text('');
          $.ajax({
            url:"/articleprocess",
            type:'POST',
            dataType:'json',
            contentType:'application/json',
            data: JSON.stringify({ 
              'quarter' : $('.qt').text(),
              'com_id' : $('.hidden_com_id2').attr('value'),
              'category_id' : $('.category').text(),
              'issue_id' : $(this).attr('value')
            }),
            context: this,
            success:function(data){
              console.log(data)
              $('#articleul').html('');
              data.forEach(element => {
                console.log(element[0])
                var plusli2 = document.createElement('li');
                plusli2.style.cssText = 'margin:5px;display:block;';
                //  기사 이미지, 기사 제목, 언론사 이름, 날짜 element[19]element[4]element[2]element[1]
                plusli2.innerHTML = '<a class = "article" href = "'+element[17]+'" target = "_target" style="display:block;width:100%;color:black"><img style = "object-fit:cover;margin-right:10px;width : 160px;height:110px"src= "'+ element[19] + '" align = "left">'+element[4]+'<br><span style="font-size:12px">'+element[16].slice(0,80)+'...</span></a><span class = "article2" style = "color:black;font-weight:lighter;font-size:10px">'+element[2]+' '+element[1]+'</span><br><hr>';
                
                $('#articleul').append(plusli2);
              });
            },
            error: function(err){
              $('.article').text("err.....");
            }
          }); 
        
        }
        plusli.append(plusa);
        var linebreak = document.createElement('hr');
        plusli.append(linebreak);
        $('#issueul').append(plusli);
      });
    },
    error: function(err){
      console.log('err');
    }
  }); 
})



//이슈 바꾸기
$('.issue').on('click',function(){
  console.log('clicked');
  $('.article').text('');
  $('.article2').text('');
  $.ajax({
    url:"/articleprocess",
    type:'POST',
    dataType:'json',
    contentType:'application/json',
    data: JSON.stringify({ 
      'quarter' : $('.qt').text(),
      'com_id' : $('.hidden_com_id2').attr('value'),
      'category_id' : $('.category').text(),
      'issue_id' : $(this).attr('value')
    }),
    context: this,
    success:function(data){
      console.log(data)
      $('#articleul').html('');
      data.forEach(element => {
        console.log(element[0])
        var plusli = document.createElement('li');
        plusli.style.cssText = 'margin:5px;display:block;';
        //  기사 이미지, 기사 제목, 언론사 이름, 날짜 element[19]element[4]element[2]element[1]
        plusli.innerHTML = '<a class = "article" href = "'+element[17]+'" style="display:block;width:100%;color:black"><img style = "object-fit:cover;margin-right:10px;width : 160px;height:110px"src= "'+ element[19] + '" align = "left">'+element[4]+'<br><span style="color:black;font-size:12px; font-weight: lighter">'+element[16].slice(0,80)+'...</span></a><span class = "article2" style = "font-size:10px">'+element[2]+' '+element[1]+'</span><br><hr>';
        
        $('#articleul').append(plusli);
      });
    },
    error: function(err){
      $('.article').text("err.....");
    }
  }); 
});



//마우스오버시 마우스 위치에 이미지 띄우기
$(document).ready(function() {
                 
  var xOffset = 30;
  var yOffset = 30;

  $(document).on("mouseover",".infobtn",function(e){ //마우스 오버시
					
    $("body").append("<p id='preview'><img src='"+ $('.test').attr("src") +"' width='400px' /></p>"); //보여줄 이미지를 선언						 
    $("#preview")
      .css("top",(e.pageY + 30) + "px")
      .css("left",(e.pageX + yOffset) + "px")
      .fadeIn("fast"); //미리보기 화면 설정 셋팅
  });
  
  $(document).on("mousemove",".infobtn",function(e){ //마우스 이동시
    $("#preview")
      .css("top",(e.pageY + 30) + "px")
      .css("left",(e.pageX + yOffset) + "px");
  });
  
  $(document).on("mouseout",".infobtn",function(){ //마우스 아웃시
    $("#preview").remove();
  });
   
});

//마우스오버시 마우스 위치에 이미지 띄우기2
$(document).ready(function() {
                 
  var xOffset = 30;
  var yOffset = 30;

  $(document).on("mouseover",".infobtn2",function(e){ //마우스 오버시
					
    $("body").append("<p id='preview'><img src='"+ $('.test2').attr("src") +"' width='400px' /></p>"); //보여줄 이미지를 선언						 
    $("#preview")
      .css("top",(e.pageY + 30) + "px")
      .css("left",(e.pageX + yOffset) + "px")
      .fadeIn("fast"); //미리보기 화면 설정 셋팅
  });
  
  $(document).on("mousemove",".infobtn2",function(e){ //마우스 이동시
    $("#preview")
      .css("top",(e.pageY + 30) + "px")
      .css("left",(e.pageX + yOffset) + "px");
  });
  
  $(document).on("mouseout",".infobtn2",function(){ //마우스 아웃시
    $("#preview").remove();
  });
   
});