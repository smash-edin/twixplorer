import {useRef, useState, useEffect} from "react"
import useAuth from "../hooks/useAuth";
import {Button} from 'semantic-ui-react';
import axios from "../api/axios";
import {useLocation, useNavigate} from "react-router-dom";

/*
axios.defaults.headers.common['Accept'] = 'application/json';
axios.defaults.headers.common['Content-Type'] = 'application/json;charset=utf-8';
axios.defaults.headers.common['Access-Control-Allow-Origin'] = '*';
axios.defaults.headers.common['Access-Control-Allow-Credentials'] = true;


axios.defaults.headers.post['Accept'] = 'application/json';
axios.defaults.headers.post['Content-Type'] = 'application/json;charset=utf-8';
axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
axios.defaults.headers.post['Access-Control-Allow-Credentials'] = true;

axios.defaults.headers.get['Accept'] = 'application/json';
axios.defaults.headers.get['Content-Type'] = 'application/json;charset=utf-8';
axios.defaults.headers.get['Access-Control-Allow-Origin'] = '*';
axios.defaults.headers.get['Access-Control-Allow-Credentials'] = true;
*/
const LOGIN_URL = '/auth';

const Login = () => {
    const setAuth = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const from = location?.state?.from || location?.state?.from?.pathname || "/analysis"

    const userRef = useRef();
    const errRef = useRef();

    const [user, setUser] = useState('');
    const [pwd, setPwd] = useState('');
    const [consumed, setConsumed] = useState(false);
    const [errMsg, setErrMsg] = useState('');

    console.log('consumed', consumed);

    if (!(consumed)) {
        try {
            if (setAuth.accessToken !== null && setAuth.accessToken !== "") {
                navigate(from, {replace: true});
            } else {
                axios.get(LOGIN_URL, {cookie: true, withCredentials: true})
                    .then(response => {
                        if (response?.data?.accessToken !== null && response?.data?.accessToken !== "") {
                            setAuth.login(response?.data?.accessToken, response?.data?.username, response?.data?.userType);
                            setUser('');
                            setPwd('');
                            navigate(from, {replace: true});
                        }
                        return response;
                    }).catch(err => {
                    console.log("HERE!" + err)
                })
            }
        } catch {
            console.log("User not found!");
        }
        setConsumed(true);
    }

    useEffect(() => {
        setErrMsg('');
    }, [user, pwd]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        await axios.post(LOGIN_URL,
            {user, pwd}, {
                cookie: true, withCredentials: true
            }).then(response => {
            console.log(response)
            if (response?.data?.accessToken !== null && response?.data?.accessToken !== "") {
                setAuth.login(response?.data?.accessToken, response?.data?.username, response?.data?.userType);
                setUser('');
                setPwd('');
                setConsumed(true);
                navigate(from, {replace: true});
            } else {
                console.log("not Success!!!")
            }
        }).catch((err) => {
            if (!err?.response) {
                console.log("-----")
                console.log(err);
                console.log("=====")
                setErrMsg('No server response');

            } else if (err.response?.status === 400) {
                setErrMsg('Missing Username or Password');
            } else if (err.response?.status === 401) {
                setErrMsg('Unauthorized');
            } else {
                setErrMsg('Login Failed!');
            }
            errRef.current.focus();
        })
    };

    return (
        <>
            <br/>
            {!setAuth.accessToken ? (
                <section>
                    <p ref={errRef} className={errMsg ? "errmsg" : "offscreen"} aria-live="assertive">{errMsg}</p>
                    <h1> Sign In</h1>
                    <form onSubmit={handleSubmit}>

                        <label htmlFor="username">Username:</label>
                        <input
                            type="text"
                            id="username"
                            ref={userRef}
                            autoComplete="off"
                            autoFocus={true}
                            onChange={(e) => setUser(e.target.value)}
                            value={user}
                            required/>

                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            onChange={(e) => setPwd(e.target.value)}
                            value={pwd}
                            required/>

                        <br/>
                        <Button className="SubmitButton">Sign In</Button>

                    </form>
                </section>
            ) : (
                <></>
            )
            }
        </>
    )
}
export default Login