/**
 * Created by python on 18-6-25.
 */
vm = new Vue({
        el: "#app",
        data: {
            // 数据
            username: '',
            image_code: '',
            image_code_id: '',
            image_code_url: '',
            mobile: '',
            sms_code: '',
            password: '',
            password2: "",
            user_id: '',
            sending_flag: false,
            // 错误信息显示
            error_username: false,
            error_image_code: false,
            error_mobile: false,
            error_sms_code: false,
            error_password: false,
            error_password2: false,
            // 错误信息
            username_error: '输入不能为空',
            image_code_error: '输入不能为空',
            mobile_error: '输入不能为空',
            sms_code_error: '输入不能为空',
            password_error: '输入不能为空',
            password2_error: '输入不能为空',
            sms_code_tip: "发送验证码",
            // 表单联级显示
            form_first_show: true,
            form_second_show: false,
            form_third_show: false,
            form_fourth_show: false,
            // 进度条显示
            step_class: {
                'step step-1': true,
                'step step-2': false,
                'step step-3': false,
                'step step-4': false,
            }
        },
        created: function () {
            this.get_image_code();
        },
        methods: {
            check_username: function () {
                if (!vm.username) {
                    vm.username_error = '输入不能为空';
                    vm.error_username = true
                }
                else {
                    vm.error_username = false
                }
            },
            check_image_code: function () {
                if (!vm.image_code) {
                    vm.image_code_error = '输入不能为空';
                    vm.error_image_code = true
                }
                else {
                    vm.error_image_code = false
                }
            },
            check_mobile: function () {
                if (!vm.mobile) {
                    vm.mobile_error = '手机号不能为空';
                    vm.error_mobile = true
                }
                else {
                    vm.error_mobile = false
                }
            },
            check_sms_code: function () {
                if (!vm.sms_code) {
                    vm.sms_code_error = '手机号不能为空';
                    vm.error_sms_code = true
                }
                else {
                    vm.error_sms_code = false
                }
            },
            check_password: function () {
                var len = vm.password.length;
                if (len < 8 || len > 20) {
                    vm.error_password = true;
                } else {
                    vm.error_password = false;
                }
            },
            check_password2: function () {
                if (vm.password != vm.password2) {
                    vm.error_password2 = true;
                } else {
                    vm.error_password2 = false;
                }
            },
            // 生成uuid
            generate_uuid: function () {
                var d = new Date().getTime();
                if (window.performance && typeof window.performance.now === "function") {
                    d += performance.now(); //use high-precision timer if available
                }
                var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                    var r = (d + Math.random() * 16) % 16 | 0;
                    d = Math.floor(d / 16);
                    return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
                });
                return uuid;
            },
            // 获取图片验证码
            get_image_code: function () {
                this.image_code_id = this.generate_uuid();
                this.image_code_url = host + "/users/image_codes/" + this.image_code_id + "/"
            },
            first_submit: function () {
                vm.check_username();
                vm.check_image_code();
                if (vm.error_username == false && vm.error_image_code == false) {
                    axios.get(host + '/users/image_code/' + vm.username + '/?image_code_id=' + vm.image_code_id + '&image_code=' + vm.image_code)
                        .then(response => {
                            sessionStorage.token = response.data.token;
                            vm.mobile = response.data.mobile;
                            vm.form_first_show = false;
                            vm.form_second_show = true;
                            vm.step_class['step step-2'] = true;
                        })
                        .catch(error => {
                            if (error.response.status = 400) {
                                if (error.response.data.username_error) {
                                    vm.username_error = error.response.data.username_error;
                                    vm.error_username = true;
                                }
                                else if (typeof error.response.data.image_code_error == "string") {
                                    vm.image_code_error = error.response.data.image_code_error;
                                    vm.error_image_code = true;
                                }
                                else {
                                    console.log(error.response.data.image_code);
                                    vm.image_code_error = error.response.data.image_code[0];
                                    vm.error_image_code = true;
                                }
                            }
                        })
                }
            },
            second_get_sms_code: function () {
                // 声明一个点击发送短信的状态，
                if (vm.sending_flag == true) {
                    return;
                }
                vm.sending_flag = true;
                vm.check_mobile();
                if (vm.error_mobile == false) {
                    axios.get(host + '/users/sms_code/?token=' + sessionStorage.token)
                        .then(response => {
                            sessionStorage.token = response.data.token;
                            // 倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
                            let num = 60;
                            // 设置一个计时器
                            let t = setInterval(() => {
                                if (num == 1) {
                                    // 如果计时器到最后, 清除计时器对象
                                    clearInterval(t);
                                    // 将点击获取验证码的按钮展示的文本回复成原始文本
                                    vm.sms_code_tip = '获取短信验证码';
                                    // 将点击按钮的onclick事件函数恢复回去
                                    vm.sending_flag = false;
                                } else {
                                    num -= 1;
                                    // 展示倒计时信息
                                    vm.sms_code_tip = num + '秒';
                                }
                            }, 1000);

                        })
                        .catch(error => {
                            if (error.response.status = 400) {
                                if (error.response.data.mobile_error) {
                                    vm.mobile_error = error.response.data.mobile_error;
                                    vm.error_mobile = true;
                                }
                                else if (error.response.data.sms_code_error) {
                                    vm.sms_code_error = error.response.data.sms_code_error;
                                    vm.error_sms_code = true;
                                }
                            }
                        })
                }
            },
            second_submit: function () {
                vm.check_sms_code();
                if (vm.error_sms_code == false) {
                    axios.get(host + '/users/accounts/' + vm.username + "/password/token/?sms_code=" + vm.sms_code)
                        .then(response => {
                            vm.user_id = response.data.id
                            sessionStorage.token = response.data.token;
                            vm.form_second_show = false;
                            vm.form_third_show = true;
                            vm.step_class['step step-3'] = true;
                        })
                        .catch(error => {
                            if (error.response.status = 400) {
                                if (error.response.data.mobile_error) {
                                    vm.mobile_error = error.response.data.mobile_error;
                                    vm.error_mobile = true;
                                }
                                else if (error.response.data.sms_code_error) {
                                    vm.sms_code_error = error.response.data.sms_code_error;
                                    vm.error_sms_code = true;
                                }
                            }
                        })
                }
            },
            third_submit: function () {
                vm.check_password();
                vm.check_password2();
                if (vm.error_password == false && vm.error_password2 == false) {
                    axios.post(host + '/users/' + vm.user_id + '/password/', {
                        password: vm.password,
                        password2: vm.password2,
                        token: sessionStorage.token
                    }, {
                        responseType: 'json'
                    })
                        .then(response => {
                            vm.form_third_show = false;
                            vm.form_fourth_show = true;
                            vm.step_class['step step-4'] = true;
                            setTimeout(function () {
                                location.href = '/login.html'
                            }, 800)
                        })
                        .catch(error => {
                            console.log(error.response.data);
                        })
                }
            }
        },
    }
);