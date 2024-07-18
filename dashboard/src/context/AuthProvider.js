import { createContext, useState } from "react";

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
    const [accessToken, setAccessToken] = useState(null);
    const [username, setUserName] = useState(null);
    const [userType, setUserType] = useState(null);

    const login = (accessToken, username, userType) =>{
        setAccessToken(accessToken)
        setUserName(username)
        setUserType(userType)
    }
    
    const logout = () =>{
        setAccessToken(null)
        setUserName(null)
        setUserType(null)
    }

    return(
        <AuthContext.Provider value={{ accessToken, username, userType, login, logout }}>
            { children }
        </AuthContext.Provider>
    )
}
export default AuthContext;