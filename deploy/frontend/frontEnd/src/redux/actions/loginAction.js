//用户登录相关的action定义
export const LOGIN_REQUEST = "LOGIN_REQUEST"
export const LOGIN_SUCCESS = "LOGIN_SUCCESS"
export const LOGIN_FAILURE = "LOGIN_FAILURE"

function requestLogin(userInfo){
    return{
        type:LOGIN_REQUEST,
        isFetching:true,
        isAuthenticated:false,
        userInfo
    }
}

function receiveLogin(user){
    return{
        type:LOGIN_SUCCESS,
        isFetching:false,
        isAuthenticated:true,
        token:user.token
    }
}

function loginError(message){
    return{
        type:LOGIN_FAILURE,
        isFetching:false,
        isAuthenticated:false,
        message
    }
}

export function login(userInfo){
    console.log("userInfo.username",userInfo.username)
    let authDate = window.btoa(userInfo.username + ':' + userInfo.password)
    console.log("authDate",authDate)
    // if(localStorage.getItem('initialized')){
    // }
    let config = {
        method: "GET",
        mode: "cors",
        headers:{
            'Authorization':`Basic ${authDate}`,
            'Access-Control-Request-Method':'*'
        }
    }
    console.log("authDate",authDate)

    return dispatch =>{
        dispatch(requestLogin(userInfo))
        
        return fetch(`http://localhost:19000/login`,config)
        .then(response => response.json()
            .then(data =>({data,response}))
            ).then(({data,response})=>{
                if(!response.ok){
                    // 登录失败的情况下，提示错误消息
                    console.log("data.message: " + data.message)
                    dispatch(loginError(data.message))
                    return Promise.reject(data)
                }else{
                    console.log("data.token: " + data.token)
                    sessionStorage.setItem('access_token',data.token)
                    localStorage.setItem('initialized',"localhost:19000")
                    dispatch(receiveLogin(data))
                }
            }).catch(err => console.log("Error: ",err))
    }
}