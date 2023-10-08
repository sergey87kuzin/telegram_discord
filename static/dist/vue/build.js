"use strict";

var _this17 = void 0;

var profile = document.getElementById("profile");

if (!!profile) {
  var vue_profile = new Vue({
    delimiters: ["[[", "]]"],
    el: "#profile",
    name: "profile",
    data: {
      phone_number: "",
      products: [],
      order: [],
      discount_value: 0,
      certificate_discount_value: 0,
      isSubscription: null
    },
    methods: {
      get_order_url: function get_order_url(order_id) {
        return "api/orders/order/".concat(order_id, "/");
      },
      subscribe_email_newsletter: function subscribe_email_newsletter() {
        var _this31 = this;

        var url = $("#profile").data("users-email-newsletter");
        var data = {
          "user": parseInt($("#profile").data("users-id")),
          "is_active": !this.isSubscription
        };
        $.ajax({
          url: url,
          method: "post",
          contentType: "application/json; charset=utf-8",
          data: JSON.stringify(data),
          success: function success(data) {
            _this31.isSubscription = !_this31.isSubscription;
          }
        });
      },
      get_detail_order: function get_detail_order(order_id) {
        var _this32 = this;

        $(".mslistorder-output").fadeOut();
        var base_url = window.location.href;
        var url = "";

        if (base_url.includes("/en/")) {
          url = window.location.origin + "/en/" + this.get_order_url(order_id);
        } else {
          url = window.location.origin + "/" + this.get_order_url(order_id);
        }

        $.ajax({
          url: url,
          method: "get",
          contentType: "application/json; charset=utf-8",
          success: function success(data) {
            $(".mslistorder-output").fadeIn(100);
            _this32.products = data.products;
            _this32.order = data;
            _this32.discount_value = parseInt(_this32.order.cost_in_currencies[data["order_currency"]]["discount_value"]);
            _this32.certificate_discount_value = parseInt(_this32.order.cost_in_currencies[data["order_currency"]]["certificate_discount_value"]);
            $("#mslistorders").hide();
          },
          error: function error(data) {// console.log(data);
          }
        });
      },
      create_review: function create_review(order_id) {
        var _this33 = this;

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

        var url = $("#profile").data("review-create");
        var data = {
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
          success: function success(data) {
            _this33.order.is_reviewed = true;
            $("#reviewSuccess").fadeIn();
          }
        });
      },
      save_profile: function save_profile() {
        var date = $("#date_mask").val() || null;
        var name = $("#name").val();
        var surname = $("#surname").val();
        var patronymic = $("#patronymic").val();
        var size = $("#size-input").attr("data-id");
        var url = $("#profile").data("profile");
        var phone = this.phone_number;
        var data = {
          date_of_birth: date,
          first_name: name,
          last_name: surname,
          patronymic: patronymic,
          size: size
        };

        if (phone.length > 0) {
          data.phone = phone;
        }

        var location_url = window.location.href;
        var msg = "";

        if (location_url.includes("/en/")) {
          msg = "Profile updated";
        } else {
          msg = "Профиль обновлен";
        }

        $.ajax({
          url: url,
          method: "put",
          contentType: "application/json; charset=utf-8",
          data: JSON.stringify(data),
          success: function success(data) {
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
          error: function error(data) {
            var key;

            for (var k in data.responseJSON) {
              key = data.responseJSON[k];
              break;
            }

            $(".updprof-error").css("color", "red").text(key); // "Ошибка во время обновления профиля, попробуйте снова");

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
      change_password: function change_password() {
        var old_password = document.getElementById("password_old") ? document.getElementById("password_old").value : null;
        var new_password = document.getElementById("password_new").value;
        var password_new_confirm = document.getElementById("password_new_confirm").value;

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

        var url = $("#profile").data("users-change-password");
        $.ajax({
          url: url,
          method: "put",
          contentType: "application/json; charset=utf-8",
          data: JSON.stringify(data),
          success: function success(data) {
            $(".updprof-error").css("display", "block");
            $("#password_old").val(null);
            $("#password_new").val(null);
            $("#password_new_confirm").val(null);
          },
          error: function error(data) {
            $("#passwordOldError").text(data.responseJSON.old_password);
            $("#passwordOldError").text(data.responseJSON.non_field_errors);
            $("#passwordNewError").text(data.responseJSON.new_password);
          }
        });
      }
    },
    created: function created() {
      var isSubscription = $("#user_subscribe").data("active");
      this.isSubscription = isSubscription === "True" ? true : false;
    },
    mounted: function mounted() {
      var _this34 = this;

      setTimeout(function () {
        var input = document.querySelector("#profile-phone");
        var phone = $("#profile-phone");
        var profile = _this34;
        var iti = window.intlTelInput(input, {
          utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.12/js/utils.js",
          nationalMode: false,
          formatOnDisplay: true,
          autoHideDialCode: false,
          initialCountry: "ru",
          preferredCountries: ["ru", "by", "kz", "az", "uz", "am", "ge", "kg"],
          geoIpLookup: function geoIpLookup(callback) {
            $.get("//ipinfo.io", function () {}, "jsonp").always(function (resp) {
              var countryCode = resp && resp.country ? resp.country : "";
              callback(countryCode);
            });
          }
        });

        var reset = function reset() {
          phone.removeClass("err-intl");
          $("input[name=\"login-updprof-btn\"]").prop("disabled", false);
        }; // on blur: validate


        phone.on("blur keyup change", function () {
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

        var handleChange = function handleChange() {
          profile.phone_number = iti.getNumber();
        };

        input.addEventListener("change", handleChange);
        input.addEventListener("keyup", handleChange);
      }, 2000);
    }
  });
}
