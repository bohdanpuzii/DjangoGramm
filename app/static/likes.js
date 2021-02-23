$('.btn-success').click(function(){
var id;
id = $(this).attr("data-catid");
$.ajax(
{
    type:"POST",
    url: "/like/"+id,
    data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
    dataType : "json",
success: function( data )
{
$('#like'+id+' span').html(data.likes_count)
$('#unlike'+id+' span').html(data.dislikes_count)
} }) });

$('.btn-danger').click(function(){
var id;
id = $(this).attr("data-catid");
$.ajax(
{
    type:"POST",
    url: "/unlike/"+id,
    data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
    dataType : "json",
success: function( data )
{
$('#like'+id+' span').html(data.likes_count)
$('#unlike'+id+' span').html(data.dislikes_count)
} }) });