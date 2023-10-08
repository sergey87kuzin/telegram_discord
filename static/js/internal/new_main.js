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
    // AJAX FIX
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

    $(document).on("click", ".select-city__modal-btn", function (e) {
        e.preventDefault();
        const city_name = $("#autodetect-city").text();
        const url = $(this).data("url");
        $.ajax({
            url: url,
            method: "post",
            data: {"city": city_name},
            success: function (data) {
                if (data.success === true) {
                    location.reload();
                } else {
                    alert("Ошибка при выборе города");
                }
            },
            error: function (data) {
                alert("Ошибка при выборе города");
            }
        });
    });

    $(document).on("click", ".select-city__cities-value", function (e) {
        e.preventDefault();
        const city_name = $(this).text();
        const url = $(this).data("url");
        $.ajax({
            url: url,
            method: "post",
            data: {"city": city_name},
            success: function (data) {
                if (data.success === true) {
                    window.location.reload(true);
                } else {
                    alert("Ошибка при выборе города");
                }
            },
            error: function (data) {
                alert("Ошибка при выборе города");
            }
        });
    });

    // Подсказки города
    // Замените на свой API-ключ
    let token = "c66ecbfcebf9ebf518852462d38deb0b1b9ce87d";

    let defaultFormatResult = $.Suggestions.prototype.formatResult;

    function formatResult(value, currentValue, suggestion, options) {
        let newValue = suggestion.data.city;
        suggestion.value = newValue;
        return defaultFormatResult.call(this, newValue, currentValue, suggestion, options);
    }

    function formatSelected(suggestion) {
        return suggestion.data.city;
    }
    const lang = window.location.href.includes("/en/") ? "en" : "ru";
    $(".select-city__cities-input").suggestions({
        token: token,
        type: "ADDRESS",
        deferRequestBy: 350,
        minChars: 3,
        hint: false,
        language: lang,
        bounds: "city",
        constraints: {
            locations: {city_type_full: "город", country: "*"}
        },
        formatResult: formatResult,
        formatSelected: formatSelected,
        onSelect: function (suggestion) {
            const city_name = suggestion.data.city;
            const url = $(".select-city__cities-input").data("url");
            $.ajax({
                url: url,
                method: "post",
                data: {"city": city_name},
                success: function (data) {
                    if (data.success === true) {
                        location.reload();
                    } else {
                        alert("Ошибка при выборе города, данного города нет в базе, выберите ближайший");
                    }
                },
                error: function (data) {
                    alert("Ошибка при выборе города, данного города нет в базе, выберите ближайший");
                }
            });
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

    if (window.ApplePaySession) { //проверка устройства
        const merchantIdentifier = 'CloudPayments_4048608';
        const promise = ApplePaySession.canMakePaymentsWithActiveCard(merchantIdentifier);
        promise.then(function (canMakePayments) {
            if (canMakePayments) {
                $('#apple-pay').show(); //кнопка Apple Pay
            }
        });
    }

    function display_sizes(class_name) {
        const block = $(class_name);
        if(!!block && block.length > 0) {
            $.post(block.data("url")).then(function(data) {
                block.html(data);
            })
        }
    }

    display_sizes(".ajax-get-sizes");


    $(document).on('click', '#apple-pay', function (){
        const product_id = $(this).data("product-id");
        const product_name = $(this).data("product-name");
        const is_en = window.location.href.includes("/en/");
        const size_id = $(".size-item-wrapper.active").find("input").val();
        if (!size_id){
            if($(".n-product__fixed").hasClass("show")) {
                display_sizes(".ajax-fixed-sizes");
                $(".n-product__fixed-size").addClass("show");
                $(".n-product__fixed").addClass("shadow");
                $("body").addClass("no-scroll");
            }
            return
        }

        const size_name = $(".size-item-wrapper.active").find("label").text().replace(/\s/g , "");
        let shippingOption = "";
        const product_price = parseInt($(this).data("price"));
        let delivery_price = 0;

        function get_apple_pay_total() {
            return product_price + delivery_price
        }

        let total_price = get_apple_pay_total;

        function getShippingOptions(shippingCountry){
            if (shippingCountry === "RU") {
                shippingOption = [{label: 'СДЭК', amount: delivery_price, 'identifier': 'cdek'}];
            } else {
                shippingOption = [{label: 'DHL', amount: delivery_price, 'identifier': 'dhl'}];
            }
        }

        const country_code = is_en ? "USA" : "RU";
        const currency = is_en ? "USD" : "RUB";
        const request = {
            requiredShippingContactFields: ['email', 'postalAddress', 'phone', 'name'],
            countryCode: country_code,
            currencyCode: currency,
            supportedNetworks: ['visa', 'masterCard'],
            merchantCapabilities: ['supports3DS'],
            lineItems: [{label: `${product_name} - ${size_name}`, amount: product_price }, {label: 'Доставка', amount: delivery_price }],
            //Назначение платежа указывайте только латиницей!
            total: { label: `Оплата заказа`, amount: total_price().toFixed('2') }, //назначение платежа и сумма
        }
        const session = new ApplePaySession(1, request);

        // обработчик события для создания merchant session.
        session.onvalidatemerchant = function (event) {
            const data = {
                validationUrl: event.validationURL
            };
            // отправьте запрос на ваш сервер, а далее запросите API CloudPayments
            // для запуска сессии
            $.post("/api/orders/apple-pay/start/", data).then(function (result) {
                session.completeMerchantValidation(result.Model);
            });
        };

        // обработчик смены адреса доставки
        session.onshippingcontactselected = function(event) {
            $.post("/api/orders/apple-pay/delivery/", {
                product: product_id,
                country_code: event.shippingContact.countryCode,
                city: event.shippingContact.locality,
                postal_code: event.shippingContact.postalCode,
            }).then(function (result) {
                delivery_price = parseFloat(result.delivery_price)
                getShippingOptions( event.shippingContact.countryCode )
                const status = ApplePaySession.STATUS_SUCCESS;
                const newTotal = { type: 'final', label: 'Оплата заказа', amount: get_apple_pay_total() };
                const newLineItems =[{type: 'final',label: product_name, amount: product_price }, {type: 'final',label: 'Доставка', amount: delivery_price }];
                session.completeShippingContactSelection(status, [], newTotal, newLineItems);
            });
        }




        // обработчик события авторизации платежа
        session.onpaymentauthorized = function (event) {

            //var email = event.payment.shippingContact.emailAddress; //если был запрошен адрес e-mail
            //var phone = event.payment.shippingContact.phoneNumber; //если был запрошен телефон
            //все варианты смотрите на сайте https://developer.apple.com/reference/applepayjs/paymentcontact
            const data = {
                cryptogram: JSON.stringify(event.payment.token),
                email: event.payment.shippingContact.emailAddress,
                phone: event.payment.shippingContact.phoneNumber,
                product: product_id,
                size: size_id,
                first_name: event.payment.shippingContact.givenName,
                last_name: event.payment.shippingContact.familyName,
                locale: is_en ? 'en' : 'ru',
                address: event.payment.shippingContact.addressLines.join(),
                index: event.payment.shippingContact.postalCode,
                city: event.payment.shippingContact.locality,
                cost: product_price,
                delivery_cost: delivery_price,
                country_iso: event.payment.shippingContact.countryCode
            };
            //передайте полученный токен на бэкэнд сервера и оттуда выполните
            //запрос  оплаты по криптограмме https://developers.cloudpayments.ru/#oplata-po-kriptogramme,
            //используя этот токен в параметре CardCryptogramPacket
            $.post("/api/orders/apple-pay/pay/", data).then(function (result) {
                if(!result.is_error){
                    session.completePayment(ApplePaySession.STATUS_SUCCESS);
                    location.href = result.redirect_url;
                }else{
                    session.completePayment(ApplePaySession.STATUS_FAILURE);
                }
            });
        };
        // Начало сессии Apple Pay
        session.begin();
    });
    // ajax registration
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
