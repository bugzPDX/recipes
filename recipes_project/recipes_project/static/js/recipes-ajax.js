$(document).ready(function(){
    // JQuery code to be added in here.
    $('#likes').click(function(){
    var catid;
    catid = $(this).attr("data-catid");
    $.get('/like_category/', {category_id: catid}, function(data){
               $('#like_count').html(data);
               $('#likes').hide();
           });
});
    $('#suggestion').keyup(function(){
            var query;
            query = $(this).val();
            $.get('/suggest_category/', {suggestion: query}, function(data){
                $('#cats').html(data);
            });
    });

$('#recipe_suggest').keyup(function(){
            var query;
            query = $(this).val();
            catid = $(this).attr("data-catid");
            $.get('/suggest_recipe/', {recipe_suggest: query, category_id: catid}, function(data){
                $('#recps').html(data);
            });
    });

    $('.recipes-add').click(function(){
        var catid = $(this).attr("data-catid");
        var url = $(this).attr("data-url");
        var title = $(this).attr("data-title");
        var me = $(this)
            $.get('/auto_add_recipe/', {category_id: catid, url: url, title: title}, function(data){
                $('#recps').html(data);
                me.hide();
            });
    });

});
