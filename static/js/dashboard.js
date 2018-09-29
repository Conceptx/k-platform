//Hide Sections
$(".sec").hide();
$("chart").hide();

setTimeout(function () {
  $("chart").fadeIn();
}, 3000);

setTimeout(function () {
  $(".sec").fadeIn();

  //Hide preloader
  $(".preloader").fadeOut();

  M.AutoInit();
  $(".approve").click(function () {
    Materialize.toast("Comment Approved", 3000);
  });

  $(".deny").click(function () {
    Materialize.toast("Comment Denied", 3000);
  });
  //Counters
  $(".count").each(function () {
    $(this)
      .prop("Counter", 0)
      .animate({
        Counter: $(this).text()
      }, {
        duration: 2000,
        easing: "swing",
        step: function (now) {
          $(this).text(Math.ceil(now));
        }
      });
  });
}, 3000);


//Task List

$("#task-form").submit(function (e) {
  const output = `
            <li class="collection-item">
                <div> ${$("#task").val()}
                    <a href="#!" class="secondary-content delete">
                        <i class="material-icons">close</i>
                    </a>
                </div>
            </li>
            `;
  $(".tasks").append(output);
  Materialize.toast("Task Added", 1000);

  e.preventDefault();
});