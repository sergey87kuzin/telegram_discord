const profile = document.getElementById("profile");

if (!!profile) {
    const vue_profile = new Vue({
        delimiters: ["[[", "]]"],
        el: "#profile",
        name: "profile",
        data: {
            phone_number: "",
            products: [],
            order: [],
            discount_value: 0,
            certificate_discount_value: 0,
            isSubscription: null,
        },
        methods: {
            get_order_url(order_id) {
                return `api/orders/order/${order_id}/`;
            },
            subscribe_email_newsletter() {
                const url = $("#profile").data("users-email-newsletter");
                const data = {
                    "user": parseInt($("#profile").data("users-id")),
                    "is_active": !this.isSubscription,
                };
                $.ajax({
                    url: url,
                    method: "post",
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: (data) => {
                        this.isSubscription = !this.isSubscription
                    }
                });
            },
            get_detail_order(order_id) {
                $(".mslistorder-output").fadeOut();
                let base_url = window.location.href;
                let url = "";
                if (base_url.includes("/en/")) {
                    url = window.location.origin + "/en/" + this.get_order_url(order_id);
                } else {
                    url = window.location.origin + "/" + this.get_order_url(order_id);
                }
                $.ajax({
                    url: url,
                    method: "get",
                    contentType: "application/json; charset=utf-8",
                    success: (data) => {
                        $(".mslistorder-output").fadeIn(100);
                        this.products = data.products;
                        this.order = data;
                        this.discount_value = parseInt(this.order.cost_in_currencies[data["order_currency"]]["discount_value"])
                        this.certificate_discount_value = parseInt(this.order.cost_in_currencies[data["order_currency"]]["certificate_discount_value"])
                        $("#mslistorders").hide();
                    },
                    error: (data) => {
                        // console.log(data);
                    }
                });
            },
            create_review(order_id) {
                var product_quality = $("input[name='product_quality']:checked").val();
                var service_quality = $("input[name='service_quality']:checked").val();
                if (!product_quality) {
                    $(".error_product_quality").text("Укажите значение");
                    return;
                }
                if (!service_quality) {
                    $(".error_service_quality").text("Укажите значение");
                    return;
                }
                const url = $("#profile").data("review-create");
                const data = {
                    "order": order_id,
                    "product_quality": product_quality,
                    "service_quality": service_quality,
                    "comment": "123"
                };
                $.ajax({
                    url: url,
                    method: "post",
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: (data) => {
                        this.order.is_reviewed = true;
                        $("#reviewSuccess").fadeIn();
                    }
                });
            },
            save_profile() {
                const date = $("#date_mask").val() || null;
                const name = $("#name").val();
                const surname = $("#surname").val();
                const patronymic = $("#patronymic").val();
                const size = $("#size-input").attr("data-id");
                const url = $("#profile").data("profile");
                var phone = this.phone_number;
                const data = {
                    date_of_birth: date,
                    first_name: name,
                    last_name: surname,
                    patronymic: patronymic,
                    size: size
                };

                if (phone.length > 0) {
                    data.phone = phone;
                }
                let location_url = window.location.href;
                let msg = "";
                if (location_url.includes("/en/")) {
                    msg = "Profile updated"
                } else {
                    msg = "Профиль обновлен"
                }
                $.ajax({
                    url: url,
                    method: "put",
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: (data) => {
                        $(".updprof-error").css("color", "green").text(msg);
                        /*
                        $("#notificationMainBackground").css({ "background-color": "green" }).fadeIn();
                        $("#notificationMainMessage").text(msg);
                        $("#notificationMainClose").css({ "color": "white" });
                        $("#notificationMainMessage").css({ "color": "white" });
                        setTimeout(function() {
                            $("#notificationMainBackground").fadeOut();
                        }, 6000);
                         */
                    },
                    error: (data) => {
                        var key;
                        for (var k in data.responseJSON) {
                            key = data.responseJSON[k];
                            break;
                        }
                        $(".updprof-error").css("color", "red").text(key);
                            // "Ошибка во время обновления профиля, попробуйте снова");
                        /*
                        $("#notificationMainBackground").css({ "background-color": "red" }).fadeIn();
                        $("#notificationMainMessage").text(data.responseJSON[key]);
                        $("#notificationMainClose").css({ "color": "white" });
                        $("#notificationMainMessage").css({ "color": "white" });
                        setTimeout(function() {
                            $("#notificationMainBackground").fadeOut();
                        }, 6000);
                         */
                    }
                });
            },
            change_password() {
                const old_password = document.getElementById("password_old") ? document.getElementById("password_old").value : null;
                const new_password = document.getElementById("password_new").value;
                const password_new_confirm = document.getElementById("password_new_confirm").value;
                if (old_password) {
                    var data = {
                        old_password: old_password,
                        new_password: new_password
                    };
                } else {
                    var data = {
                        new_password: new_password
                    };
                }
                ;
                $("#passwordOldError").text(null);
                $("#passwordNewError").text(null);
                $("#passwordNewConfirmError").text(null);
                $(".updprof-error").fadeOut();
                if (password_new_confirm !== new_password) {
                    $("#passwordNewConfirmError").text("Пароли не совпадают");
                    return;
                }
                const url = $("#profile").data("users-change-password");
                $.ajax({
                    url: url,
                    method: "put",
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    success: (data) => {
                        $(".updprof-error").css("display", "block");
                        $("#password_old").val(null);
                        $("#password_new").val(null);
                        $("#password_new_confirm").val(null);
                    },
                    error: (data) => {
                        $("#passwordOldError").text(data.responseJSON.old_password);
                        $("#passwordOldError").text(data.responseJSON.non_field_errors);
                        $("#passwordNewError").text(data.responseJSON.new_password);
                    }
                });
            }
        },
        created() {
            const isSubscription = $("#user_subscribe").data("active")
            this.isSubscription = isSubscription === "True" ? true : false
        },
        mounted() {
            setTimeout(() => {
                var input = document.querySelector("#profile-phone");
                var phone = $("#profile-phone");
                const profile = this;
                var iti = window.intlTelInput(input, {
                    utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.12/js/utils.js",
                    nationalMode: false,
                    formatOnDisplay: true,
                    autoHideDialCode: false,
                    initialCountry: "ru",
                    preferredCountries: ["ru", "by", "kz", "az", "uz", "am", "ge", "kg"],
                    geoIpLookup: function(callback) {
                        $.get("//ipinfo.io", function() {
                        }, "jsonp").always(function(resp) {
                            var countryCode = (resp && resp.country) ? resp.country : "";
                            callback(countryCode);
                        });
                    }
                });

                const reset = function() {
                    phone.removeClass("err-intl");
                    $("input[name=\"login-updprof-btn\"]").prop("disabled", false);
                };

                // on blur: validate
                phone.on("blur keyup change", function() {
                    if ($.trim(phone.val())) {
                        if (iti.isValidNumber()) {
                            reset();
                        } else {
                            phone.addClass("err-intl");
                            $("input[name=\"login-updprof-btn\"]").prop("disabled", true);
                        }
                    } else {
                        reset();
                    }
                });
                const handleChange = function() {
                    profile.phone_number = iti.getNumber();
                };
                input.addEventListener("change", handleChange);
                input.addEventListener("keyup", handleChange);
            }, 2000)
        }
    });
}