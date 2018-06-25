var vm = new Vue({
        el: '#app',
        data: {
            error_name: false,
            error_password: false,
            error_check_password: false,
            error_phone: false,
            error_allow: false,
            error_image_code: false,
            error_sms_code: false,

            username: '',
            password: '',
            password2: '',
            mobile: '',
            image_code: '',
            image_code_id: '',
            image_code_url: '',
            sms_code: '',
            allow: false,
            sending_flag: false,
            name_error: '请输入5-20个字符的用户',
            image_code_error: "请填写图片验证码",
            sms_code_error: "请填写短信验证码",
            mobile_error: "您输入的手机号格式不正确",
            sms_code_tip: '获取短信验证码',
            allow_error: '请勾选同意'
        },
        // 实例生命周期,挂在dom前请求验证码
        mounted: function () {
            this.get_image_code();
        }
        ,
        methods: {
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
                this.image_code_url = host+"/users/image_codes/" + this.image_code_id + "/"
            },
            // 获取短信验证码
            get_sms_code: function () {
                // 声明一个点击发送短信的状态，
                if (vm.sending_flag == true) {
                    return;
                }
                vm.sending_flag = true;

                // 校验参数，保证输入框有数据填写
                vm.check_phone();
                vm.check_image_code();

                if (vm.error_phone == true || vm.error_image_code == true) {
                    vm.sending_flag = false;
                    return;
                }
                axios.get(host+"/users/sms_codes/" + vm.mobile + "/" + "?image_code_id=" + vm.image_code_id + "&&image_code=" + vm.image_code, {responseType: 'json'})
                    .then(response => {
                        // 表示后端发送短信成功
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
                        }, 1000, 60);

                    })
                    .catch(error => {
                            console.log(error.response.data);
                            if (error.response.status = 401) {
                                if (error.response.data.image_code_error) {
                                    vm.image_code_error = error.response.data.image_code_error;
                                    vm.error_image_code = true
                                }
                                else {
                                    vm.mobile_error = error.response.data.sms_code_error;
                                    vm.error_phone = true
                                }
                            }
                            vm.sending_flag = false;
                        }
                    );
            },
            check_username: function () {
                var len = this.username.length;
                if (len < 5 || len > 20) {
                    this.error_name = true;
                }
                else {
                    this.error_name = false;
                    axios.get(host+"/users/usernames/" + vm.username + "/")
                        .then(response => {
                            if (response.data.username_error) {
                                vm.name_error = response.data.username_error;
                                vm.error_name = true
                            }
                        })
                        .catch(error => {

                        })

                }
            },
            check_pwd: function () {
                var len = this.password.length;
                if (len < 8 || len > 20) {
                    this.error_password = true;
                } else {
                    this.error_password = false;
                }
            },
            check_cpwd: function () {
                if (this.password != this.password2) {
                    this.error_check_password = true;
                } else {
                    this.error_check_password = false;
                }
            },
            check_phone: function () {
                var re = /^1[345789]\d{9}$/;
                if (re.test(this.mobile)) {
                    this.error_phone = false;
                    axios.get(host+"/users/usermobiles/" + vm.mobile + "/")
                        .then(response => {
                            if (response.data.mobile_error) {
                                vm.mobile_error = response.data.mobile_error;
                                vm.error_phone = true
                            }
                        })
                        .catch(error => {

                        })


                } else {
                    this.error_phone = true;
                    vm.sending_flag = false;
                }
            },
            check_image_code: function () {
                if (!this.image_code) {
                    this.error_image_code = true;
                    vm.sending_flag = false;

                } else {
                    this.error_image_code = false;
                }
            },
            check_sms_code: function () {
                if (!this.sms_code) {
                    this.error_sms_code = true;
                } else {
                    this.error_sms_code = false;
                }
            },
            check_allow: function () {
                if (!this.allow) {
                    this.error_allow = true;
                } else {
                    this.error_allow = false;
                }
            },
            // 注册
            on_submit: function () {
                this.check_username();
                this.check_pwd();
                this.check_cpwd();
                this.check_phone();
                this.check_sms_code();
                this.check_allow();
                if (vm.error_name == false && vm.error_password == false && vm.error_check_password == false && vm.error_phone == false && vm.error_allow == false && vm.error_image_code == false && vm.error_sms_code == false) {
                    axios.post(host+"/users/", {
                        'username': vm.username,
                        'mobile': vm.mobile,
                        'password': vm.password,
                        'password2': vm.password2,
                        'sms_code': vm.sms_code,
                        'allow': vm.allow.toString(),

                    }, {
                        responseType: 'json'
                    })
                        .then(response => {
                            //注册成功后将后端返回的token信息储存在localstorage(本地化储存)中/sessionstorage(浏览器关闭即消失)中
                            localStorage.clear();
                            sessionStorage.clear();
                            localStorage.token = response.data.token;
                            location.href = '/index.html'
                        })
                        .catch(error => {
                                if (error.response.status = 400) {
                                    if (error.response.data.sms_code) {
                                        vm.sms_code_error = error.response.data.sms_code[0];
                                        vm.error_sms_code = true;
                                    }
                                    else if (error.response.data.username) {
                                        vm.name_error = error.response.data.username[0];
                                        vm.error_name = true;
                                    }
                                    else if (error.response.data.non_field_errors) {
                                        vm.sms_code_error = error.response.data.non_field_errors[0];
                                        vm.error_sms_code = true;
                                    }

                                    else if (error.response.data.image_code_error) {
                                        vm.image_code_error = error.response.data.image_code_error;
                                        vm.error_image_code = true
                                    }
                                    else {
                                        console.log(error.response.data);
                                        // vm.sms_code_error = error.response.data.sms_code[0];
                                        // vm.error_sms_code = true;
                                    }
                                }

                            }
                        )
                }
            }
        }
    })
    ;
