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

    $.ajaxSetup({
         beforeSend: function (xhr, settings) {
             function getCookie(name) {
                 let cookieValue = null;
                 if (document.cookie && document.cookie !== "") {
                     let cookies = document.cookie.split(";");
                     for (let i = 0; i < cookies.length; i++) {
                         let cookie = $.trim(cookies[i]);
                         // Does this cookie string begin with the name we want?
                         if (cookie.substring(0, name.length + 1) === (name + "=")) {
                             cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                             break;
                         }
                     }
                 }
                 return cookieValue;
             }


             if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                 // Only send the token to relative URLs i.e. locally.
                 xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
             }
         }
     });

     $(document).on('submit', '.ajax-login-form', function (e) {
         e.preventDefault()
         const data = $(this).serialize();
         const url = $(this).data("url");
         $.ajax({
             url: url,
             data: data,
             method: "post",
             success: function (data) {
                 if (!!data.error) {
                     const tpl = data.tpl;
                     $(".modal-login__extended").html(tpl);
                 } else {
                     window.location.href = data.url
                 }
             },
             error: function (data) {
                 alert("Error on authorization");
             }
         });
     })

     function clear_error_fields(element_array) {
         element_array.forEach(function (error_fild) {
             $(error_fild).text("");
         })
     }

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
