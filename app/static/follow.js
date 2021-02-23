$('.btn-secondary').click(function(){
var id;
id = $(this).attr("data-catid");
console.log(id)
$.ajax(
{
    type:"POST",
    url: "/follow/"+id,
    data : {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
    dataType : "json",
success: function( data )
{
if (data.followed){
$('#follow'+id+' span').html('Unfollow')
}
else{
$('#follow'+id+' span').html('Follow')
}

} }) });