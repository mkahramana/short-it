function copyToClipboard(id) {
    var $tempTextArea = $("<textarea>");
    $("body").append($tempTextArea);
    $tempTextArea.val($(id).text()).select();
    document.execCommand("copy");
    $tempTextArea.remove();
}