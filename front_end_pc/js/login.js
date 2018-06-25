/**
 * Created by python on 18-6-23.
 */
var vm = new Vue({
    el: '#app',
    data: {
        error_username: false,
        error_pwd: false,
        remember_info: false,
        username: '',
        password: '',
        remember: '',
        username_error: '请填写用户名或手机号',
        password_error: '请输入密码',
        token: ''
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
        check_username: function () {
            if (!this.username) {
                this.error_username = true
            }
            else {
                this.error_username = false
            }
        },
        check_pwd: function () {
            if (!this.password) {
                this.error_pwd = true
            }
            else {
                this.error_pwd = false
            }
        },
        on_submit: function () {
            this.check_username();
            this.check_pwd();
            if (vm.error_username == false && vm.error_pwd == false) {
                axios.post(host + '/users/authorizations/', {
                    'username': vm.username,
                    'password': vm.password,
                })
                    .then(response => {
                        localStorage.clear();
                        sessionStorage.clear();
                        if (vm.remember_info) {
                            localStorage.token = response.data.token;
                        }
                        else {
                            sessionStorage.token = response.data.token;
                        }
                        // 跳转页面
                        var return_url = this.get_query_string('next');
                        if (!return_url) {
                            return_url = '/index.html';
                        }
                        location.href = return_url;

                    })
                    .catch(error => {
                        console.log(error.data)
                    })
            }
        }
    }
});