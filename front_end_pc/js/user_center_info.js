/**
 * Created by python on 18-6-29.
 */
var vm = new Vue({
    el: '#app',
    data: {
        host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: '',
        mobile: '',
        email: '',
        email_active: false,
        set_email: false,
        send_email_btn_disabled: false,
        send_email_tip: '重新发送验证邮件',
        email_error: false,
        error_email: '邮箱格式错误'
    },
    mounted: function () {
        // 判断用户的登录状态
        console.log(this.token);
        // console.log(token);
        if (this.user_id && this.token) {
            axios.get(host + '/users/user/', {
                // 将JWT token用headers传递到服务器
                headers: {
                    'Authorization': 'JWT ' + this.token
                },
                responseType: 'json',
            })
                .then(response => {
                    // 加载用户数据
                    this.user_id = response.data.id;
                    this.username = response.data.username;
                    this.mobile = response.data.mobile;
                    // 邮箱内容是否为空决定页面是否显示input框
                    this.email = response.data.email;
                    // 邮箱激活状态决定是否发送验证邮件
                    this.email_active = response.data.email_active;
                })
                .catch(error => {
                    if (error.response.status == 401 || error.response.status == 403) {
                        // 400错误则跳转到登录页面
                        location.href = '/login.html?next=/user_center_info.html';
                    }
                });
        } else {
            location.href = '/login.html?next=/user_center_info.html';
        }
    },
    methods: {
        // 退出
        logout: function () {
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 保存email
        save_email: function () {
            var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
            if (re.test(this.email)) {
                this.email_error = false;
            } else {
                this.email_error = true;
                return;
            }
            axios.put(this.host + '/users/emails/',
                {email: this.email}, {
                    headers: {
                        // 用于登录权限认证
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json'
                })
                .then(response => {
                    this.set_email = false;
                    this.send_email_btn_disabled = true;
                    this.send_email_tip = '已发送验证邮件'
                })
                .catch(error => {
                    if (error.response.status == 400) {
                        if (error.response.data) {
                            vm.error_email = error.response.data.email[0];
                            vm.email_error = true;
                        }
                    }
                    console.log(error.response.data);
                });
        }
    }
});