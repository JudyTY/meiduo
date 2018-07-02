var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: sessionStorage.username || localStorage.username,
        is_show_edit: false,
        edit: false,
        provinces: [],
        cities: [],
        districts: [],
        addresses: [],
        limit: '',
        default_address_id: '',
        form_address: {
            receiver: '',
            province_id: '',
            city_id: '',
            district_id: '',
            address: '',
            phone: '',
            tel: '',
            email: '',
            user_id: ''
        },
        error_receiver: false,
        error_place: false,
        error_mobile: false,
        error_email: false,
        editing_address_index: '', // 正在编辑的地址在addresses中的下标，''表示新增地址
        is_set_title: [],
        input_title: ''
    },
    mounted: function () {
        axios.get(this.host + '/areas/', {
            // 页面加载完成时将省级行政区的列表查询出来
            responseType: 'json'
        })
            .then(response => {
                this.provinces = response.data;
            })
            .catch(error => {
                alert(error.response.data);
            });
        this.get_addresses();

    },
    watch: {
        // 监听所选的省级行政区和市级行政区的id是否发生改变,改变时,则使用此id查询行政区的详细页,获取下级列表
        'form_address.province_id': function () {
            if (this.form_address.province_id) {
                axios.get(this.host + '/areas/' + this.form_address.province_id + '/', {
                    responseType: 'json'
                })
                    .then(response => {
                        this.cities = response.data.subs;
                    })
                    .catch(error => {
                        console.log(error.response.data);
                        this.cities = [];
                    });
            }
        },
        'form_address.city_id': function () {
            if (this.form_address.city_id) {
                axios.get(this.host + '/areas/' + this.form_address.city_id + '/', {
                    responseType: 'json'
                })
                    .then(response => {
                        this.districts = response.data.subs;
                    })
                    .catch(error => {
                        console.log(error.response.data);
                        this.districts = [];
                    });
            }
        }
    },
    methods: {
        // 退出
        logout: function () {
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        clear_all_errors: function () {
            this.error_receiver = false;
            this.error_mobile = false;
            this.error_place = false;
            this.error_email = false;
        },
        // 展示新增地址界面
        show_add: function () {
            this.clear_all_errors();
            this.editing_address_index = '';
            this.form_address.receiver = '';
            this.form_address.province_id = '';
            this.form_address.city_id = '';
            this.form_address.district_id = '';
            this.form_address.address = '';
            this.form_address.phone = '';
            this.form_address.tel = '';
            this.form_address.email = '';
            this.is_show_edit = true;
        },
        // 展示编辑地址界面
        show_edit: function (index) {
            this.clear_all_errors();
            this.editing_address_index = index;

            // 只获取数据，防止修改form_address影响到addresses数据
            for (i in this.addresses) {
                if (this.addresses[i].id == index) {
                    this.form_address = JSON.parse(JSON.stringify(this.addresses[i]));
                }
            }
            this.is_show_edit = true;
            vm.edit = true;

        },
        check_receiver: function () {
            if (!this.form_address.receiver) {
                this.error_receiver = true;
            } else {
                this.error_receiver = false;
            }
        },
        check_place: function () {
            if (!this.form_address.place) {
                this.error_place = true;
            } else {
                this.error_place = false;
            }
        },
        check_mobile: function () {
            var re = /^1[345789]\d{9}$/;
            if (re.test(this.form_address.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile = true;
            }
        },
        check_email: function () {
            if (this.form_address.email) {
                var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
                if (re.test(this.form_address.email)) {
                    this.error_email = false;
                } else {
                    this.error_email = true;
                }
            }
        },
        // 保存地址
        save_address: function () {
            if (vm.edit == false) {
                vm.form_address.user_id = vm.user_id;
                axios.post(this.host + '/address/', vm.form_address)
                    .then(response => {
                        vm.is_show_edit = false;
                        this.get_addresses();
                    })
                    .catch(error => {
                        console.log(error.response.data);
                    });
            }
            else {
                vm.form_address.user_id = vm.user_id;
                axios.put(this.host + '/address/' + this.editing_address_index + '/', vm.form_address)
                    .then(response => {
                        vm.is_show_edit = false;

                        this.get_addresses();

                    })
                    .catch(error => {
                        console.log(error.response.data);
                    });
                vm.edit = false;

            }

        },
        // 删除地址
        del_address: function (index) {
            axios.delete(this.host + '/address/' + index + '/')
                .then(response => {
                    this.get_addresses();

                })
                .catch(error => {
                    console.log(error.response.data);
                });

        },
        // 设置默认地址
        set_default: function (index) {
            axios.put(this.host + '/users/'+vm.user_id+'/userdefaultaddress/',{
                'address_id':index
            })
                .then(response => {
                    vm.default_address_id=index
                })
                .catch(error => {
                });

        },
        // 展示编辑标题
        show_edit_title: function (index) {


        },
        // 保存地址标题
        save_title: function (index) {

        },
        // 取消保存地址
        cancel_title: function (index) {

        },
        // 查询收货地址
        get_addresses: function () {
            axios.get(this.host + '/address/?id=' + this.user_id)
                .then(response => {
                    vm.addresses = response.data.addresses;
                    vm.limit = response.data.limit;
                    vm.default_address_id = response.data.default_address_id
                })
                .then(error => {
                    console.log(error.response.data)
                })

        }
    }
});