import { NavLink, useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import axios from "../api/axios";
const LOGOUT_URL = '/logout';


export const Navbar = () => {
    const navLinkStyles = ({isActive}) => {
        return {
            fontWeight: isActive ? 'bold' : 'normal',
            textDecotation: isActive ? 'none' : 'underline',
            fontSize: 'x-large',
            margin: 10
        }
    }
    const setAuth = useAuth();
    const navigate = useNavigate();
    const handleLogout = async () =>{
        await axios.post(LOGOUT_URL,{timeout: 5000} );
        setAuth.logout()
        navigate("/analysis")
    }
    return(
        <nav className='primary-nav'>
            <NavLink style={navLinkStyles} className='.navigation-menu ul' to='/analysis'>
                Analysis
            </NavLink>

            <NavLink style={navLinkStyles} to='/help'>
                Help
            </NavLink>

            {setAuth.userType === 'admin' ? (
                <NavLink style={navLinkStyles} to='/admin'>
                    Admin
                </NavLink>
            ):(
                <></>
            )}
            {setAuth.accessToken ?  (
                <>
                    <NavLink style={navLinkStyles} to='/load_report'>
                        Load Report
                    </NavLink>
                    <button onClick={handleLogout}>Logout</button>
                </>
            ) : (
                <NavLink style={navLinkStyles}  to='/login'>
                Login
            </NavLink>
            )
            }
            
        </nav>
    )
}