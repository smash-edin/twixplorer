import {useState, useEffect} from 'react';
import {Button, Input, Popup, Icon} from "semantic-ui-react";
import axios from "../api/axios";
import {DataGrid} from '@mui/x-data-grid';
import useAuth from '../hooks/useAuth';
import {useNavigate} from 'react-router-dom';

const ADMIN_ADDUSER_URL = "/register_user"
const ADMIN_GETUSERS_URL = "/get_users"
const ADMIN_DELUSER_URL = "/delete_user"
const ADMIN_URL = '/admin';
const LOGIN_PAGE = '/login';

export const Admin = () => {
    const setAuth = useAuth();
    const navigate = useNavigate();

    const [response, setResponse] = useState([]);

    useEffect(() => {
        async function fetchData() {
            try {
                if (setAuth.accessToken) {
                    const res = await axios.get(ADMIN_URL, {timeout: 15000});
                    setResponse(res)
                    setAuth.login(res?.data?.accessToken, res?.data?.username, res?.data?.userType)
                } else {
                    navigate(LOGIN_PAGE, {state: {from: ADMIN_URL}});
                }
            } catch (err) {
                console.log("err: ", setAuth.userType);
            }
        }

        fetchData();
    }, []);


    const [loading, setLoading] = useState(false)
    const [ready, setReady] = useState(false)
    const [username, setUsername] = useState("")
    const [usernameError, setUsernameError] = useState("")
    const [password, setPassword] = useState("")
    const [passwordError, setPasswordError] = useState("")
    const [showPassword, setShowPassword] = useState(false);

    const [usersTable, setUsersTable] = useState({});
    const [selectedRows, setSelectedRows] = useState([]);

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    const handleSelectionChange = (selectionModel) => {
        if (selectionModel.length > 0) {
            setSelectedRows(selectionModel);
        } else {
            setSelectedRows([]);
        }
    };

    const handleSelectAll = () => {
        const currentPageRows = usersTable.rows.slice(
            usersTable.pageSize * usersTable.page,
            usersTable.pageSize * (usersTable.page + 1)
        );
        const currentPageRowIds = currentPageRows.map(row => row.id);
        setSelectedRows(currentPageRowIds);
    };
    useEffect(() => {
        if (/[^0-9a-zA-Z_@\-$&]/.test(username)) {
            setUsernameError("Only characters, digits and these special chars (_@-$&) are allowed")
        } else {
            setUsernameError("")
        }
        if (/[^0-9a-zA-Z_@\-$&]/.test(password)) {
            setPasswordError("Only characters, digits and these special chars (_@-$&) are allowed")
        } else {
            setPasswordError("")
        }

        setReady((username.length >= 4 && password.length >= 6))
    }, [username, password]);

    const deleteUsers = async () => {
        await axios.post(ADMIN_DELUSER_URL,
            JSON.stringify({"users": selectedRows,})).then(() => {
            submitGetUsers()
        })
            .catch(function (error) {
                console.log("responses didnt work")
                if (error.response) {
                    if (error.response.status === 401) {
                        alert("401 error, please login before continuing")
                    } else if (error.response.status === 409) {
                        alert("User name already exists! Please choose another name.")
                    } else {
                        console.log(error.response)
                    }
                }
                setLoading(false)
            });
    }

    // Async function that posts the query to the API to get the necessary info to generate the report
    const submitAddUser = async () => {
        await axios.post(ADMIN_ADDUSER_URL,
            JSON.stringify({"uname": username, "pwd": password,}), {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'WithCredentials': true,
                }
            }).then((data_resp => {
            if (data_resp.hits > 0) {
                console.log("data_resp: " + data_resp)
            } else {
                console.log("NO data_resp found!")
            }
            submitGetUsers()
            setLoading(false)
        }))
            .catch(function (error) {
                console.log("responses didnt work")
                if (error.response) {
                    if (error.response.status === 401) {
                        alert("Not authorised to access, you will be redirected to the correct page!")
                        window.open('/login')
                    } else if (error.response.status === 409) {
                        alert("User name already exists! Please choose another name.")
                    } else {
                        console.log(error.response)
                    }
                }
                setLoading(false)
            });
    }

    const submitGetUsers = async () => {
        await axios.post(ADMIN_GETUSERS_URL,
            JSON.stringify({"uname": username, "pwd": password,}), {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'WithCredentials': true,
                }
            }).then(response => {
            if (response) {
                if (response?.data) {
                    const formatData = (data) => {
                        let rows = data.users
                        let heightType = "auto"
                        let columns = [
                            {
                                field: 'username',
                                width: 90,
                                align: "left",
                                headerAlign: 'center',
                                renderHeader: () => (<strong>Username</strong>),
                            },
                            {
                                field: 'type',
                                width: 75,
                                headerAlign: 'center',
                                align: 'center',
                                renderHeader: () => (<strong>Type</strong>),
                            },
                        ];

                        return {"rows": rows, "columns": columns, "heightType": heightType}
                    };
                    setUsersTable(formatData(response.data))
                }
            } else {
                console.log("NO data_resp found!")
            }
            setLoading(false)
        })
            .catch(function (error) {
                console.log("responses didnt work")
                if (error.response) {
                    if (error.response.status === 401) {
                        alert("Not authorised to access, you will be redirected to the correct page!")
                        window.open('/login')
                    } else {
                        console.log(error.response)
                    }
                }
                setLoading(false)

            });
    }


    return (
        <main className="App">
            {
                setAuth.accessToken && setAuth.userType === 'admin' ? (
                    <>
                        {response?.data?.message}
                        <header className="Input">
                            <div className="PageTitle">
                                <h1>TwiXplorer - Admin</h1>
                                <Popup
                                    content="This page allows the administrator of the dashboard to manage access to the tool by other users."
                                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                                />
                            </div>
                            <div className="InputFields">
                                <div className="SubTitleWithPopup">
                                    <h2>Current Users</h2>
                                    <Popup
                                      content="To view a table of existing users, click on the 'Get Current Users' button. Select users and click on the 'Delete Selected User' button to delete their account. By default, users are shown in group of 5. Click on arrows at the bottom right of the table to navigate to the next page of users."
                                      trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                                    />
                                </div>
                                <div className="SubmitButton">
                                    <Button
                                        onClick={() => {
                                            setLoading(true)
                                            submitGetUsers()
                                        }}
                                        loading={loading}
                                    >Get Current Users</Button>

                                </div>
                            </div>

                            {usersTable["rows"] !== undefined && usersTable["rows"] !== null && usersTable["rows"].length > 0 &&
                                <div className='InputFields'>
                                    <div className="TopContent">
                                        <DataGrid
                                            getRowHeight={() => usersTable["heightType"]}
                                            rows={usersTable["rows"]}
                                            columns={usersTable["columns"]}
                                            initialState={{
                                                ...usersTable.initialState,
                                                pagination: {paginationModel: {pageSize: 5}},
                                            }}
                                            checkboxSelection
                                            onRowSelectionModelChange={handleSelectionChange}
                                            onSelectionModelChange={handleSelectionChange}
                                            pageSizeOptions={[5, 10, 15]}
                                            selectionModel={selectedRows}

                                        />
                                        <div className="SubmitButton">
                                            <button onClick={deleteUsers}>Delete Selected
                                                User{selectedRows.length > 1 && 's'} </button>
                                        </div>
                                    </div>
                                </div>
                            }
                            <div className="InputFields">
                                <div className="SubTitleWithPopup">
                                    <h2>Add User</h2>
                                    <Popup
                                      content="To register a new user, provide a username in the 'Username' field, an associated password in the 'Password' field and click on the 'Add User' button."
                                      trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                                    />
                                </div>
                                <div className="TitleWithPopup">
                                    <h3>Username</h3><h3 style={{marginRight: "5px"}}></h3>
                                    <Popup
                                        content="The user name of the new user. Only letters and digits are allowed."
                                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                                        </div>}
                                    />
                                    <Input
                                        placeholder="Username"
                                        type="text"
                                        value={username}
                                        onChange={(e, {value}) => setUsername(value)}
                                        className="usernameInput"
                                    />
                                    <div className='Error' style={{
                                        marginLeft: "5px",
                                        marginTop: "10px",
                                        color: "red"
                                    }}>{usernameError}</div>
                                </div>

                                <div className="TitleWithPopup">
                                    <h3>Password</h3><h3 style={{marginRight: "5px"}}></h3>
                                    <Popup
                                        content="The password for the new user."
                                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/>
                                        </div>}
                                    />

                                    <Input
                                        type={showPassword ? 'text' : 'password'}
                                        value={password}
                                        onChange={(e, {value}) => setPassword(value)}
                                        icon={
                                            <Icon
                                                name={showPassword ? 'eye slash outline' : 'eye'}
                                                link
                                                onClick={togglePasswordVisibility}
                                            />
                                        }
                                        //iconPosition="left"
                                        className="passwordInput"
                                    />
                                    <div className='Error' style={{
                                        marginLeft: "5px",
                                        marginTop: "10px",
                                        color: "red"
                                    }}>{passwordError}</div>
                                </div>

                                <div className="SubmitButton">
                                    <Button
                                        onClick={() => {
                                            setLoading(true)
                                            submitAddUser()
                                        }}
                                        loading={loading}
                                        disabled={!ready}
                                    >Add User</Button>
                                </div>
                            </div>
                        </header>
                    </>
                ) : (
                    <p>
                        {"Not authenticated!"}

                    </p>
                )
            }
        </main>

    );
}
export default Admin;
