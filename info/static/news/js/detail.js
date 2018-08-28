function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    })

    // 收藏
    $(".collection").click(function () {

        var params = {

            "news_id": $(this).attr("data-newid"),

            "action": "collect"
        }
        // 发起注册请求
        $.ajax({
            // 设置url
            url: "/news/news_collect",
            // 设置请求方式
            type: "post",
            // 将js对象转换成json字符串发送给后端
            data: JSON.stringify(params),
            // 在请求头里面带上csrf_token随机值
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            // 声明上传的数据内容格式是 json字符串
            contentType: "application/json",
            dataType: "json",
            success: function (resp) {
                if (resp.errno == "0") {
                    // 收藏成功
                    // 隐藏收藏按钮
                    $(".collection").hide();
                    // 显示取消收藏按钮
                    $(".collected").show();
                } else if (resp.errno == "4101") {
                    $('.login_form_con').show();
                } else {
                    alert(resp.errmsg);
                }
            }
        })


    })
})

// 取消收藏
$(".collected").click(function () {

    var params = {

        // 获取新闻id
        "news_id": $(this).attr("data-newid"),
        // 收藏行为
        "action": "cancel_collect"
    }
    // 发起注册请求
    $.ajax({
        // 设置url
        url: "/news/news_collect",
        // 设置请求方式
        type: "post",
        // 将js对象转换成json字符串发送给后端
        data: JSON.stringify(params),
        // 在请求头里面带上csrf_token随机值
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        // 声明上传的数据内容格式是 json字符串
        contentType: "application/json",
        dataType: "json",
        success: function (resp) {
            if (resp.errno == "0") {
                // 取消收藏成功
                // 显示收藏按钮
                $(".collection").show(); // 隐藏取消收藏按钮
                $(".collected").hide();
            } else if (resp.errno == "4101") {
                $('.login_form_con').show();
            } else {
                alert(resp.errmsg);
            }
        }
    })

})

// 评论提交
$(".comment_form").submit(function (e) {
    e.preventDefault();

})

$('.comment_list_con').delegate('a,input', 'click', function () {

    var sHandler = $(this).prop('class');

    if (sHandler.indexOf('comment_reply') >= 0) {
        $(this).next().toggle();
    }

    if (sHandler.indexOf('reply_cancel') >= 0) {
        $(this).parent().toggle();
    }

    if (sHandler.indexOf('comment_up') >= 0) {
        var $this = $(this);
        if (sHandler.indexOf('has_comment_up') >= 0) {
            // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
            $this.removeClass('has_comment_up')
        } else {
            $this.addClass('has_comment_up')
        }
    }

    if (sHandler.indexOf('reply_sub') >= 0) {
        alert('回复评论')
    }
})

// 关注当前新闻作者
$(".focus").click(function () {

})

// 取消关注当前新闻作者
$(".focused").click(function () {

})
