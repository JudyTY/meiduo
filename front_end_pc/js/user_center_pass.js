/**
 * Created by python on 18-7-2.
 */
var vm = new Vue({
    el: '#app',
    data: {
        old_password: '',
        new_password: "",
        new_password2: "",
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        old_error:'',
        new_error:'',
        error_old:false,
        error_new:false
    },
    methods: {
        change_pwd: function () {
            axios.post(host + '/users/' + this.user_id + '/passwords/', {
                'old_password': this.old_password,
                'new_password': this.new_password,
                'new_password2': this.new_password2

            }, {
                headers: {
                    // 用于登录权限认证
                    'Authorization': 'JWT ' + this.token
                },
                responseType: 'json'
            })
                .then(response=>{
                    location.href='/login.html'
                })
                .catch(error=>{
                    console.log(error.response.data);
                    if(error.response.data.old_error){
                        vm.old_error=error.response.data.old_error;
                        vm.error_old = true
                    }
                    else {
                        vm.new_error=error.response.data.new_error;
                        vm.error_new = true
                    }
                })

        }
    }
});