import {LOGIN_REQUEST,LOGIN_SUCCESS,LOGIN_FAILURE} from "../actions/loginAction"
import { LOGOUT_SUCCESS } from "../actions/logoutAction";

const initialState = {
    isFetching:false,
    isAuthenticated:sessionStorage.getItem('access_token')?true:false,
    isInitialized:localStorage.getItem('initialized')?true:false,
    errorMessage:""
}

export default function auth(state = initialState, action){
    switch(action.type){
        case LOGIN_REQUEST:
            return Object.assign({},state,{
                isFetching:true,
                isAuthenticated:false,
                user:action.userInfo
            })
        case LOGIN_SUCCESS:
            return Object.assign({},state,{
                isFetching:false,
                isAuthenticated:true,
                isInitialized:true,
                errorMessage:""
            })
        case LOGIN_FAILURE:
            return Object.assign({},state,{
                isFetching:false,
                isAuthenticated:false,
                errorMessage:action.message
            })
        case LOGOUT_SUCCESS:
        return Object.assign({},state,{
            isFetching:true,
            isAuthenticated:false,
        })
        default:
            return state
    }
}