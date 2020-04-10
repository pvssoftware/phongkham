(function (a) {
  a.createModal = function (b) {
    defaults = {
      title: "",
      message: "Your Message Goes Here!",
      closeButton: true,
      submitButton: false,
      scrollable: false,
      modalSize:"modal-lg",
    };
    var b = a.extend({}, defaults, b);
    var c =
      b.scrollable === true
        ? 'style="max-height: 420px;overflow-y: auto;"'
        : "";
    html = '<div class="modal fade" id="myModal">';
    html += '<div class="modal-dialog ' +b.modalSize+'">';
    html += '<div class="modal-content">';
    html += '<div class="modal-header">';
    if (b.title.length > 0) {
      html += '<h4 class="modal-title">' + b.title + "</h4>";
    }
    html +=
      '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>';
    html += "</div>";
    html += '<div class="modal-body" id="modal-body-content"' + c + ">";
    html += b.message;
    html += "</div>";
    html += '<div class="modal-footer">';
    if (b.closeButton === true) {
      html +=
        '<button type="button" class="btn btn-secondary" data-dismiss="modal">Đóng</button>';
    }
    if (b.submitButton === true) {
      html +=
        '<button type="button" class="btn btn-finished" id="submit_bt_modal">Xác nhận</button>';
    }
    html += "</div>";
    html += "</div>";
    html += "</div>";
    html += "</div>";
    a("body").prepend(html);
    a("#myModal")
      .modal()
      .on("hidden.bs.modal", function () {
        a(this).remove();
      });
  };
})(jQuery);
