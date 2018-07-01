var vm = new Vue({
    el: '#app',
    data: {
        host,
        // 控制页面的显示
        is_show_waiting: true,

        error_password: false,
        error_phone: false,
        error_image_code: false,
        error_sms_code: false,
        error_image_code_message: '',
        error_phone_message: '',
        error_sms_code_message: '',

        image_code_id: '', // 图片验证码id
        image_code_url: '',

        sms_code_tip: '获取短信验证码',
        sending_flag: false, // 正在发送短信标志

        password: '',
        mobile: '',
        image_code: '',
        sms_code: '',
        access_token: ''
    },
    // 钩子，页面加载完成以后自动的代码
    mounted: function () {
        axios.get(host + '/oauth/qq/user/?code=' + this.get_query_string('code'), {})
            .then(response => {
                if (response.data.access_token) {
                    vm.generate_image_code();
                    vm.access_token = response.data.access_token;
                    vm.is_show_waiting = false
                }
                else {
                    location.href = '/'

                }


            })
            .catch(error => {
            })
    },
    methods: {
        // 获取url路径参数
        get_query_string: function (name) {
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
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
        // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
        generate_image_code: function () {
            vm.image_code_id = vm.generate_uuid();
            vm.image_code_url = host + '/users/image_codes/' + vm.image_code_id + '/'
        },
        check_pwd: function () {
            var len = this.password.length;
            if (len < 8 || len > 20) {
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_phone: function () {
            var re = /^1[345789]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_phone = false;
            } else {
                this.error_phone_message = '您输入的手机号格式不正确';
                this.error_phone = true;
            }
        },
        check_image_code: function () {
            if (!this.image_code) {
                this.error_image_code_message = '请填写图片验证码';
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
            }
        },
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        // 发送手机短信验证码
        send_sms_code: function () {
            if (this.sending_flag == true) {
                return;
            }
            this.sending_flag = true;

            // 校验参数，保证输入框有数据填写
            this.check_phone();
            this.check_image_code();

            if (this.error_phone == true || this.error_image_code == true) {
                this.sending_flag = false;
                return;
            }

            // 向后端接口发送请求，让后端发送短信验证码
            axios.get(host + '/users/sms_codes/' + vm.mobile + '/?image_code=' + vm.image_code + '&image_code_id=' + vm.image_code_id)

        },
        // 保存
        on_submit: function () {
            this.check_pwd();
            this.check_phone();
            this.check_sms_code();

            if (this.error_password == false && this.error_phone == false && this.error_sms_code == false) {
                axios.post(host + '/oauth/qq/user/', {
                    'access_token': vm.access_token,
                    'mobile': vm.mobile,
                    'sms_code': vm.sms_code,
                    'password': vm.password
                })
                    .then(response => {
                        if (response.data.token) {
                            // 记录用户登录状态
                            sessionStorage.clear();
                            localStorage.clear();
                            localStorage.token = response.data.token;
                            localStorage.user_id = response.data.user_id;
                            localStorage.username = response.data.username;
                            location.href = this.get_query_string('state');
                        }
                        else {
                            if (error.response.status == 400) {
                                this.error_sms_code_message = error.response.data.message;
                                this.error_sms_code = true;
                            } else {
                                console.log(error.response.data);
                            }
                        }


                    })
                    .catch(error => {
                        console.log(error.response.data)
                    })


            }
        }
    }
});