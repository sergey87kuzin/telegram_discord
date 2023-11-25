// // // // // // // // // // // // // // //
// ФАЙЛ НОВОГО JS ДЛЯ РЕФАКТОРИНГА СТАРОГО //
// // // // // // // // // // // // // // //

$(document).ready(function () {
    let location = window.location.href;
    let ru = "ru";
    let en = "/en/";
    if (navigator.language.includes(ru) && location.includes(en) && localStorage["myKey"] !== "1") {
        detectRuUserLanguage();
    } else if (!navigator.language.includes(ru) && !location.includes(en) && localStorage["myKey"] !== "1") {
        detectEnUserLanguage();
    }
});


function detectRuUserLanguage() {
    window.location.replace(window.location.origin + window.location.pathname.slice(3));
    localStorage["myKey"] = "1";
}

function detectEnUserLanguage() {
    window.location.replace(window.location.origin + '/en' + window.location.pathname);
    localStorage["myKey"] = "1";
}

$(document).ready(function () {

    $(document).on("submit", ".ajax-registration-form", function (e) {
        e.preventDefault();
        const is_loyalty = $("#is_sign_loyalty").prop('checked')
        let formData = {
            ...Object.fromEntries(new FormData(this)),
            register_in_loyalty: is_loyalty,
        }
        if (!is_loyalty) {
            delete formData.phone
            delete formData.confirmation_code
        } else if (formData.phone.length < 9) {
            if (window.location.href.includes("/en/")) {
                $(".error-registration-phone").text('Phone needs to be verified')
            } else {
                $(".error-registration-phone").text('Необходимо подтвердить телефон')
            }
            return
        }
        const data = new URLSearchParams(formData).toString();
        const url = $(this).data("url");
        const element_errors_array = [
            ".error-messages-registration",
            ".error-registration-firstname",
            ".error-registration-lastname",
            ".error-registration-date_of_birth",
            ".error-registration-email",
            ".error-registration-phone",
            ".error-registration-password1",
            ".error-registration-password2",
            ".error-registration-confirmation_code",
        ]
        clear_error_fields(element_errors_array);
        $.ajax({
            url: url,
            data: data,
            method: "post",
            success: function (data) {
                if (!!data.error) {
                    Object.entries(data.error_messages).forEach(([key, value]) => {
                        switch (key) {
                            case '__all__':
                                $(".error-messages-registration").text(value[0]);
                                return
                            case 'first_name':
                                $(".error-registration-firstname").text(value[0]);
                                return;
                            case 'last_name':
                                $(".error-registration-lastname").text(value[0]);
                                return;
                            case 'date_of_birth':
                                $(".error-registration-date_of_birth").text(value[0]);
                                return;
                            case 'email':
                                $(".error-registration-email").text(value[0]);
                                return;
                            case 'phone':
                                $(".error-registration-phone").text(value[0]);
                                return;
                            case 'password1':
                                $(".error-registration-password1").text(value[0]);
                                return;
                            case 'password2':
                                $(".error-registration-password2").text(value[0]);
                                return;
                            case 'confirmation_code':
                                $(".error-registration-confirmation_code").text(value[0]);
                                return;
                        }
                    });

                } else {
                    $(".ajax-registration-form  ").text(data.success_messages);
                }
            }
            ,
            error: function (data) {
                alert("Ошибка при авторизации! Попробуйте позже.");
            }
        });
    });

    $(document).on("submit", ".change-password__form", function (e) {
        e.preventDefault();
        const data = {};
        data.old_password = $("#password_old").val();
        data.new_password = $("#password_new").val();
        data.new_password_confirm = $("#password_new_confirm").val();

        const url = $(this).data("url");
        $.ajax({
            url: url,
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
            method: "put",
            success: function (data) {
                $("#passwordNewConfirmError").text("");
                $("#passwordNewError").text("");
                $("#passwordOldError").text("");
                $("#id-change-password-backend-error").text("");

                $("#password_old").val("");
                $("#password_new").val("");
                $("#password_new_confirm").val("");


                $("#change-password-success").show();
            },

            error: function (data) {
                $("#change-password-success").hide();

                $("#passwordNewConfirmError").text("");
                $("#passwordNewError").text("");
                $("#passwordOldError").text("");

                $("#password_old").val("");
                $("#password_new").val("");
                $("#password_new_confirm").val("");
                if (data.responseJSON.new_password_confirm) {
                    $("#passwordNewConfirmError").text(data.responseJSON.new_password_confirm[0]);
                }
                if (data.responseJSON.new_password) {
                    $("#passwordNewError").text(data.responseJSON.new_password[0]);
                }
                if (data.responseJSON.old_password) {
                    $("#passwordOldError").text(data.responseJSON.old_password[0]);
                }
                if (data.responseJSON.error) {
                    $("#id-change-password-backend-error").text(data.responseJSON.error[0]);
                }
            }
        });
    });

    $(document).on("click", "#ajaxCart2", function (e) {
        $(".wrapper-ajax-cart, .modal-overlay").addClass("active");
        $("html").css("overflow-y", "hidden");
        $("body").css("overflow-y", "hidden");
        window.modal_cart_vue.get_cart_items();
    });

    $(document).on("click", ".n-product__order-checkout", function (e) {
        $(".wrapper-ajax-cart, .modal-overlay").addClass("active");
        $("html").css("overflow-y", "hidden");
        $("body").css("overflow-y", "hidden");
        window.modal_cart_vue.get_cart_items();
    });

    $(document).on("click", ".n-product__add-basket", function (e) {
        const product_id = $(this).data("busket-id");
        const price = $(this).data("product-price");
        if (product_id) {
            window.search_vue.add_to_cart(product_id);
        }
        var _tmr = _tmr || [];
        _tmr.push({
            type: 'reachGoal',
            id: '3140222',
            value: price,
            goal: 'addToCart',
            params: { product_id }
        });
        $(".n-product__order-checkout").addClass("show");
        $(".n-product__fixed-size").removeClass("show");
        $(".n-product__fixed").removeClass("shadow");
        $("body").addClass("no-scroll");
    });

    $(document).on("click", "#addToBasket", function (e) {
        const product_id = $(this).data("busket-id");
        const price = $(this).data("product-price");
        window.add_to_cart_vue.add_to_cart(product_id);
        var _tmr = _tmr || [];
        _tmr.push({
            type: 'reachGoal',
            id: '3140222',
            value: price,
            goal: 'addToCart',
            params: { product_id }
        });
    });

    $(document).on("click", ".n-product__add-favorites", function (e) {
        const product_id = $(this).data("item-id");
        const price = $(this).data("price");
        window.add_to_cart_vue.togglefavorite(product_id);
        _tmr.push({
            type: 'reachGoal',
            id: 3140222,
            value: price,
            goal: 'addToWishlist',
            params: { product_id }
        });
    });

    $(document).on("click", ".like-good-favorite", function (e) {
        const product_id = $(this).data("item-id");
        const price = $(this).data("price");
        window.search_vue.togglefavorite(product_id);
        _tmr.push({
            type: 'reachGoal',
            id: 3140222,
            value: price,
            goal: 'addToWishlist',
            params: { product_id }
        });
    });

    $(document).on("click", "#promoCode", function (e) {
        $(this).css("display", "none");
        $("#promoCodeBtn").css("display", "block");
    });

    $(document).on("click", "#certificate", function (e) {
        $(this).css("display", "none");
        $("#certificateBtn").css("display", "block");
    });

    $(document).on("click", "#subscribeToSize", function (e) {
        const product_id = $(this).data("product-id");
        const size = $('#sizeAvailable').text();
        if ($(".n-product__fixed").length && $(".n-product__fixed").hasClass("shadow")) {
            $(".n-product__fixed").removeClass("shadow")
            $(".n-product__fixed-size").removeClass("show")
            $("body").removeClass("no-scroll")
        }
        if (!!window.search_vue) {
            window.search_vue.subscribe_to_size(product_id, size);
        } else if (!!window.cart) {
            window.new_cart.subscribe_to_size(product_id, size);
        }
    });

    $(document).on("click", "#deleteSizeSubscribe", function (e) {
        const subscribe_id = $(this).data("subscribe-id");
        window.search_vue.delete_subscribe_to_size(subscribe_id);
    });

    $(document).on("click", "#id-recover-password-button", function (e) {
        const url = $("#passwordRestore").data("restore-pasw");
        const email = $("#id-recover-password-email").val();
        const data = {
            "email": email
        };

        $.ajax({
            url: url,
            contentType: "application/json",
            data: JSON.stringify(data),
            method: "post",
            success: function (data) {
                $("#passwordRestore").text(data.result);
            },
            error: function (data) {
                var key;
                for (var k in data.responseJSON) {
                    key = k;
                    break;
                }
                $("#id-error-recover-password").text(data.responseJSON[key]);
            }
        });
    });


    $(document).on("click", "#notificationClose", function (e) {
        $("#notificationBackground").fadeOut();
    });
    $(document).on("click", "#notificationMainClose", function (e) {
        $("#notificationMainBackground").fadeOut();
    });
    $(".order__close").on("click", function () {
        $(".mslistorder-output").hide();
        $("#mslistorders").fadeIn(100);
    });


    $(document).on("click", "#feedbackSubmit", function (e) {
        const url = $("#mainContacts").data("feedbeck-create");
        $(".error_nam3_zv0n0k").text("");
        $(".error_ph0n3_zv0n0k").text("");
        $(".error_ma1l_zv0n0k").text("");
        $("#feedbackError").text("");
        $(".error_msg_zv0n0k").text("");
        let error_message = "";
        let success_message = "";
        if (url.includes("/en/")) {
            error_message = "Fill this field";
            //success_message = "Message sent";
        }
        else {
            error_message = "Заполните поле";
            //success_message = "Сообщение отправлено";
        }
        var erros = false;
        if (!$("#nam3_zv0n0k").val().length) {
            $(".error_nam3_zv0n0k").text(error_message);
            var errors = true;
        }
        if (!$("#ph0n3_zv0n0k").val().length) {
            $(".error_ph0n3_zv0n0k").text(error_message);
            var errors = true;
        }
        if (!$("#ma1l_zv0n0k").val().length) {
            $(".error_ma1l_zv0n0k").text(error_message);
            var errors = true;
        }
        if (!$("#msg_zv0n0k").val().length) {
            $(".error_msg_zv0n0k").text(error_message);
            var errors = true;
        }
        if (errors) {
            return;
        }
        const data = {
            "name": $("#nam3_zv0n0k").val(),
            "phone": $("#ph0n3_zv0n0k").val(),
            "email": $("#ma1l_zv0n0k").val(),
            "message": $("#msg_zv0n0k").val()
        };
        $.ajax({
            url: url,
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
            method: "post",
            success: function (data) {
                dataLayer.push({'event': 'feedback'});
                $("#nam3_zv0n0k").val(null);
                $("#ph0n3_zv0n0k").val(null);
                $("#ma1l_zv0n0k").val(null);
                $("#msg_zv0n0k").val(null);
                /*
                $("#notificationMainBackground").css({"background-color": "green"}).fadeIn();
                $("#notificationMainMessage").text(success_message);
                $("#notificationMainClose").css({"color": "white"});
                $("#notificationMainMessage").css({"color": "white"});
                setTimeout(function () {
                    $("#notificationMainBackground").fadeOut();
                }, 6000);
                 */
            },
            error: function (data) {
                var key;
                for (var k in data.responseJSON) {
                    key = k;
                    break;
                }
                $("#feedbackError").text(data.responseJSON[key]);
            }
        });
    });

    $(document).on("click", "#restore-password-done", function (e) {
        const url = $("#restorePasswordDone").data("restode-pswd-done");

        const password = $("#resetPasswordNew").val();
        const repeated_password = $("#resetPasswordConfirm").val();

        const urlParams = new URLSearchParams(window.location.search);
        const uid = urlParams.get("uid");
        const token = urlParams.get("restore_token");

        const data = {
            "password": password,
            "repeated_password": repeated_password,
            "uid": uid,
            "activation_token": token
        };

        $("#resetPasswordError").text("");
        $("#resetPasswordConfirmError").text("");
        $.ajax({
            url: url,
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(data),
            method: "post",
            success: function (data) {
                $("#formRestorePasw").hide();
                $("#restoreSuccess").show();
            },
            error: function (data) {
                $("#resetPasswordError").text(data.responseJSON.password);
                $("#resetPasswordError").text(data.responseJSON.non_field_errors);
                $("#resetPasswordConfirmError").text(data.responseJSON.repeated_password);
            }
        });
    });

    // $(document).ready(function () {
    //     $.datepicker.regional['ru'] = {
    //         closeText: 'Закрыть',
    //         prevText: 'Предыдущий',
    //         nextText: 'Следующий',
    //         currentText: 'Сегодня',
    //         monthNames: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
    //         monthNamesShort: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],
    //         dayNames: ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'],
    //         dayNamesShort: ['вск', 'пнд', 'втр', 'срд', 'чтв', 'птн', 'сбт'],
    //         dayNamesMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
    //         dateFormat: 'dd.mm.yy',
    //         showMonthAfterYear: false,
    //     };
    //     $.datepicker.regional["en-GB"] = {
    //         closeText: "Done",
    //         prevText: "Prev",
    //         nextText: "Next",
    //         currentText: "Today",
    //         monthNames: ["January", "February", "March", "April", "May", "June",
    //             "July", "August", "September", "October", "November", "December"],
    //         monthNamesShort: ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
    //             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    //         dayNames: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    //         dayNamesShort: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    //         dayNamesMin: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
    //         weekHeader: "Wk",
    //         dateFormat: "dd/mm/yy",
    //         firstDay: 1,
    //         isRTL: false,
    //         showMonthAfterYear: false,
    //         yearSuffix: ""
    //     };
    //
    //     $("#datepicker").on("change", function () {
    //         let hVal = $(this).val();
    //         let tDate = (new Date(hVal)).getTime() / 1000;
    //         $("#dob").val(tDate);
    //     });
    //
    //     if (window.location.href.includes("/en/")) {
    //         $.datepicker.setDefaults($.datepicker.regional["en-GB"]);
    //     } else {
    //         $.datepicker.setDefaults($.datepicker.regional["ru"]);
    //     }
    //     $("#birthday_sign").datepicker({
    //         showAnim: "show",
    //         altFormat: "yy-mm-dd",
    //         dateFormat: "dd.mm.yy",
    //         changeMonth: true,
    //         changeYear: true,
    //         yearRange: "1950:2008",
    //         defaultDate: "-25y",
    //         onSelect: function (value) {
    //             const date = new Date(value).toLocaleDateString('en-ca')
    //             $(this).attr("data-val", date)
    //         },
    //     });
    // });

    $(document).ready(function () {
        $('#date_mask').mask("99.99.9999",{placeholder:"__.__.____"});
    });

    $(document).on("click", "#restorePasswordSubmit", function (e) {
    $("#restorePasswordSuccess").text("");
    $(".loginFPErrors").text("");
    var url = $("#passwordRestore").data("restore-pasw");
    var email = $("#emailForRestore").val();
    var data = {
      "email": email
    };
    $.ajax({
      url: url,
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(data),
      method: "post",
      success: function success(data) {
        $("#restorePasswordSuccess").text(data.result);
      },
      error: function error(data) {
        $(".loginFPErrors").text(data.responseJSON.non_field_errors);
      }
    });
  });

    $(document).on("submit", '.welcome-ajax-form', function (e){
        e.preventDefault();

        const data = $(this).serialize();
        const url = $(this).data('url');
        const parent = $(this).parent();
        $.ajax({
            url: url,
            data: data,
            method: 'post',
            success: function (data){
                dataLayer.push({'event': 'email_popup'});
                $(".modal-welcome").removeClass("active");
                $(".modal-overlay").removeClass("active big-z-index");
                $("body").removeClass("no-scroll");
            },
            error: function (data){
                parent.html(data);
            }
        })
    });
})
