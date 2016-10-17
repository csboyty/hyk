var tyPhoto=(function(config,functions){
    return {
        offset:10,
        loadPhotos:function(){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.imagesGetAll,
                type:"get",
                data:{
                    offset:me.offset,
                    limit:config.perLoadCounts.list
                },
                success:function(response){
                    if(response.success){

                        var tpl=$("#tyPhotoTpl").html();
                        var html=juicer(tpl,response);
                        $("#tyPhotos .list").append(html);

                        if(response.results.length==config.perLoadCounts.list){
                            me.offset+=config.perLoadCounts.list;
                        }else{
                            me.offset=-1;
                            $(".nav1").addClass("hidden");
                        }
                    }else{
                        functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(response){
                    functions.ajaxErrorHandler();
                }
            })
        },
        init:function(){
            if($("#tyPhotos").height()<$("#tyPhotos .list").height()){
                this.offset=-1;
                $(".nav1").addClass("hidden");
            }
            var firstLi=$("#tyPhotos .list li:eq(0)");
            firstLi.addClass("active");

            if(firstLi.data("intro")){
                $("#tyPhotoDetail .showMore").removeClass("hidden");
            }else{
                $("#tyPhotoDetail .showMore").addClass("hidden");
            }
        },
        navHandler:function(el){
            var direction=el.data("direction");
            var list=$("#tyPhotos .list");
            var listHeight=list.height();
            var photoViewHeight=$("#tyPhotos").height();
            var marginTop=parseInt(list.css("marginTop"));
            var me=this;
            switch(direction){
                case "up":
                    $(".nav2").removeClass("hidden");
                    marginTop-=photoViewHeight;
                    list.animate({
                        "marginTop":marginTop+"px"
                    },200,function(){
                        if(Math.abs(marginTop)>=listHeight-photoViewHeight*2&&me.offset!=-1){
                            me.loadPhotos();
                        }
                        if(Math.abs(marginTop)+photoViewHeight>=listHeight){
                            $(".nav1").addClass("hidden");
                        }
                    });
                    break;
                case "down":
                    $(".nav1").removeClass("hidden");
                    marginTop+=photoViewHeight;
                    list.animate({
                        "marginTop":marginTop+"px"
                    },200,function(){
                        if(Math.abs(marginTop)==0){
                            $(".nav2").addClass("hidden");
                        }
                    });
                    break;
            }

        }
    }
})(config,functions);
$(document).ready(function(){
    tyPhoto.init();

    $("#tyPhotos .list").on("click","li",function(){
        $("#tyPhotoDetail img").attr("src",$(this).find("img").attr("src"));
        $("#tyPhotoDetail .content").html($(this).data("name")+"<br>"+$(this).data("intro"));
        $("#tyPhotoDetail .showMore").addClass("up").removeClass("down");
        if($(this).data("intro")){
            $("#tyPhotoDetail .showMore").removeClass("hidden");
        }else{
            $("#tyPhotoDetail .showMore").addClass("hidden");
        }
        $("#tyPhotoDetail .info").height("10px");
        $("#tyPhotos .active").removeClass("active");
        $(this).addClass("active");
        $("#currentPage").text($(this).index()+1);
    });

    $(".nav").click(function(){
        tyPhoto.navHandler($(this));
    });

    //显示描述
    $(".showMore").click(function(){
        if($(this).hasClass("up")){
            $(this).parent().height("auto");
            $(this).addClass("down").removeClass("up");
        }else{
            $(this).parent().height("10px");
            $(this).addClass("up").removeClass("down");
        }
    });
});
