var single=(function(config,functions){
  return {
      patterns:[],
      getPatterns:function(ids){
          var me=this;
          $.ajax({
              url:config.ajaxUrls.patternsGetDetail,
              dataType:"json",
              type:"get",
              data:{
                  ids:ids
              },
              success:function(response){
                  if(response.success){
                      var length=response.patterns.length;
                      for(var i=0;i<length;i++){
                          response.patterns[i].profile=
                              functions.findElInArray(me.patterns,"id",response.patterns[i].id)["profile"];
                      }

                      var tpl=$("#patternsTpl").html();
                      var tpl1=$("#patternNameTpl").html();
                      var html=juicer(tpl,response);
                      var html1=juicer(tpl1,response);
                      $("#patterns").html(html);
                      $("#patternNames").html(html1);

                  }else{
                      functions.ajaxReturnErrorHandler(response.error_code);
                  }
              },
              error:function(){
                  functions.ajaxErrorHandler();
              }
          });
      },
      getPost:function(id){
          var me=this;
          $.ajax({
              url:config.ajaxUrls.itemGetDetail.replace(":id",id),
              dataType:"json",
              type:"get",
              success:function(response){
                  if(response.success){
                      var length=response.fixture.assets.length;
                      var ids=[];
                      for(var i=0;i<length;i++){
                            if(response.fixture.assets[i].pattern_id){
                                me.patterns.push({
                                    id:response.fixture.assets[i].pattern_id,
                                    profile:response.fixture.assets[i].profile_file
                                });
                                ids.push(response.fixture.assets[i].pattern_id);
                            }
                      }
                      if(ids.length==0){
                          $("#patternsContainer").remove();
                          $("#patterNames").parent(".row").remove();
                      }else{
                          me.getPatterns(JSON.stringify(ids));
                      }
                  }else{
                      functions.ajaxReturnErrorHandler(response.error_code);
                  }
              },
              error:function(){
                  functions.ajaxErrorHandler();
              }
          });
      }
  }
})(config,functions);
$(document).ready(function(){

    single.getPost(id);

    $('#carousel').flexslider({
        animation: "slide",
        controlNav: false,
        animationLoop: false,
        slideshow: false,
        itemWidth: 120,
        itemMargin: 5,
        asNavFor: '#slider'
    });

    $('#slider').flexslider({
        animation: "slide",
        controlNav: false,
        animationLoop: false,
        slideshow: false,
        sync: "#carousel"
    });

    $('#carousel1').flexslider({
        animation: "slide",
        controlNav: false,
        animationLoop: false,
        itemWidth: 210,
        itemMargin: 5
    });


    var timer=null;
    var el=$(".aside");
    var scrollTop=0;
    $(window).scroll(function(){
        if(timer){
            clearTimeout(timer);
            timer=null;
        }
        timer=setTimeout(function(){
            scrollTop=$(window).scrollTop();
            if(scrollTop>=250){
                el.css("top",scrollTop-180);
            }else{
                el.css("top",60)
            }
        },200);
    });
});
