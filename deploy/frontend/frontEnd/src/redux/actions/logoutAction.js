//退出登录相关的action定义
export const LOGOUT_REQUEST = "LOGOUT_REQUEST"
export const LOGOUT_SUCCESS = "LOGOUT_SUCCESS"

function requestlogout(userInfo){
    return{
        type:LOGOUT_REQUEST,
        isFetching:true,
        isAuthenticated:true,
    }
}

function receivelogout(user){
    return{
        type:LOGOUT_SUCCESS,
        isFetching:false,
        isAuthenticated:false,
    }
}

export function logout(){
    return dispatch => {
        dispatch(requestlogout())
        sessionStorage.removeItem("access_token")
        dispatch(receivelogout())
    }
}