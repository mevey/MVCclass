/*
 * This is the Javascript file that makes requests to our controller.
 * We have prepared one API that makes requests in two unique ways
 * The filter option requests for data to be displayed and the download option 
 * requests for data to be in a downloadable form
 */


$('#filter-btn').click(function() {
	//Reload the page to display the new data.
	//You could optionally work with Ajax
	url = "/?name=" + $("#speaker").val() + "&year=" + $("#year").val()
    url += "&party=" + $("#party").val()
    url += "&committee=" + $("#committee").val()
    url += "&state=" + $("#state").val()
    url += "&quantile=" + $("#quantile").val()
	window.location.href=url
});

$('#download-btn').click(function() {
    url = "/?format=csv&name=" + $("#speaker").val() + "&year=" + $("#year").val()
    url += "&party=" + $("#party").val()
    url += "&committee=" + $("#committee").val()
    url += "&state=" + $("#state").val()
    url += "&quantile=" + $("#quantile").val()
	window.location.href=url
});
