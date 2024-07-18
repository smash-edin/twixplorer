import {useState, useEffect} from 'react';
import {Button, Icon, Popup} from "semantic-ui-react";
import axios from "../api/axios";
import {DataGrid} from '@mui/x-data-grid';
import useAuth from '../hooks/useAuth';
import {useNavigate} from 'react-router-dom';

const LoadReport_URL = "/load_report"
const DeleteReport_URL = "/delete_report"
const LOGIN_PAGE = '/login';

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
export const LoadReport = () => {
    const setAuth = useAuth();
    const navigate = useNavigate();
    const [response, setResponse] = useState([]);

    useEffect(() => {
        async function fetchData() {
            try {
                if (setAuth.accessToken) {
                    console.log(" --> here!", LoadReport_URL)
                    await axios.get(LoadReport_URL, {
                            withCredentials: true, timeout: 15000
                        }
                    ).then((resp) => {
                        setResponse(resp);
                        setAuth.login(resp?.data?.accessToken, resp?.data?.username, resp?.data?.userType)
                    }).catch((resp) => {
                            setResponse(resp);
                        }
                    );
                } else {
                    navigate(LOGIN_PAGE, {state: {from: LoadReport_URL}});
                }
            } catch (err) {
                setAuth.logout();
            }
        }

        fetchData();
    }, []);


    const [loading, setLoading] = useState(false)
    const [reportsTable, setReportsTable] = useState({});
    const [selectedRows, setSelectedRows] = useState([]);


    const handleSelectionChange = (selectionModel) => {
        // Assuming your DataGrid row ids are in the 'id' field
        console.log('selectionModel1:', selectionModel);

        if (selectionModel.length > 0) {
            setSelectedRows(selectionModel);
            console.log('selectedRowsData:', selectionModel);
        } else {
            setSelectedRows([]);
        }
    };

    const renderTextWithURLs = (params, dataField, labelField, url_) => {
        const text = params.row[dataField];
        const label = params.row[labelField];
        return (
            <>
                <a href={url_ + "/analysis?report=" + text} target="_blank">{label} </a>
            </>
        )
    }

    const getTermsFromToken = (params, dataField, labelField) => {
        const text = params.row[dataField];
        //const data = JSON.parse(atob(text))
        const data = JSON.parse(decodeURIComponent(text).toString())
        return (
            labelField === 'dates' ? (data['date_start'] !== null && data['date_start'] !== undefined ? data['date_start'].slice(0, 10) : "") + ' - ' + (data['date_end'] !== null && data['date_end'] !== undefined ? data['date_end'].slice(0, 10) : "") : labelField === 'keywords' ? data[labelField].join(', ') : data[labelField]
        )
    }

    const deleteReport = async () => {
        await axios.post(DeleteReport_URL,
            JSON.stringify({"reports": selectedRows,}), {
                withCredentials: true, timeout: 15000
            }
        ).then(() => {
            submitGetReports()
        }).catch(function (error) {
            console.log("responses didnt work");
            if (error.response) {
                if (error.response.status === 401) {
                    console.log("401 error, please login before continuing")
                    alert("401 error, please login before continuing")
                } else if (error.response.status === 409) {
                    console.log("User name already exists! Please choose another name.")
                    alert("User name already exists! Please choose another name.")
                } else {
                    console.log(error.response)
                }
            }
        });
        setLoading(false);
    }

    // Async function that posts the query to the API to get the necessary info to generate the report
    const submitGetReports = async () => {
        console.log("LOAD REPORT ")
        await axios.post(LoadReport_URL, {}, {withCredentials: true, timeout: 15000}).then((response) => {

            if (response?.data) {
                const formatData = (data) => {
                    const currentUrl = window.location.origin
                    console.log(currentUrl)
                    let heightType = "auto"
                    let rows = data.data
                    let columns = [
                        {
                            field: 'reportName',
                            width: 125,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Report Name</strong>),
                            renderCell: (params) => renderTextWithURLs(params, 'token', 'reportName', currentUrl)
                        },
                        {
                            field: 'username',
                            width: 100,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>User Name</strong>),
                        },
                        {
                            field: 'creationTime',
                            width: 125,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Creation Time</strong>),
                        },
                        {
                            field: 'terms',
                            width: 125,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Keywords</strong>),
                            renderCell: (params) => getTermsFromToken(params, 'token', 'keywords')
                        },
                        {
                            field: 'dataSource',
                            width: 100,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Source</strong>),
                            renderCell: (params) => getTermsFromToken(params, 'token', 'source_text')
                        },
                        {
                            field: 'sentiment',
                            width: 75,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Sentiment</strong>),
                            renderCell: (params) => getTermsFromToken(params, 'token', 'sentiment')
                        },
                        {
                            field: 'dateRange',
                            width: 175,
                            align: "left",
                            headerAlign: 'center',
                            renderHeader: () => (<strong>Date Range</strong>),
                            renderCell: (params) => getTermsFromToken(params, 'token', 'dates')
                        }
                    ];
                    return {"rows": rows, "columns": columns, "heightType": heightType}
                };

                setReportsTable(formatData(response.data))
            } else {
                console.log("NO data_resp found!")
            }
        }).catch((err) => {
            console.log("responses didnt work")
            if (err.status === 401) {
                console.log("401 error, please login before continuing")
                alert("401 error, please login before continuing")
            } else if (err.status === 409) {
                console.log("User name already exists! Please choose another name.")
                alert("User name already exists! Please choose another name.")
            } else {
                console.log(err)
            }
        });
        setLoading(false);
    };

    return (
        <main className="App">
            {
                setAuth.accessToken ? (
                    <>
                        {response?.data?.message}
                        <header className="Input">
                            <div className="PageTitle">
                                <h1>TwiXplorer - Load Reports</h1>
                                <Popup
                                  content="This page allows the analyst to view searches they have saved via the 'Save report' button on the 'Analysis page' and load them again in a new tab. Click on the 'Get Reports' button to load the table containing saved past searches/reports. Each row displays the name of the report, as defined by the analyst when they saved their search, the values for the input filters originally used to create the report (i.e. source dataset, keywords, dates, sentiment) and the date the report was saved. Clicking on a report name will re-generated it in a new tab. The saved report can take from a few seconds to a few minutes to load. Select reports and click on the 'Delete Selected Reports' button to delete them. Click on arrows at the bottom right of the table to navigate to the next page of results. To sort or filter the table, hover over a column header and click on the three dots."
                                  trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                                />
                            </div>
                            <div className="InputFields">
                                <div className="SubmitButton">
                                    <Button
                                        onClick={() => {
                                            setLoading(true)
                                            submitGetReports()
                                        }}
                                        loading={loading}
                                    >Get Reports</Button>

                                </div>
                            </div>

                            {reportsTable["rows"] !== undefined && reportsTable["rows"] !== null && reportsTable["rows"].length > 0 &&
                                <div className='InputFields'>
                                    <div className="TopContent">
                                        <DataGrid
                                            getRowHeight={() => reportsTable["heightType"]}
                                            rows={reportsTable["rows"]}
                                            columns={reportsTable["columns"]}
                                            initialState={{
                                                ...reportsTable.initialState,
                                                pagination: {paginationModel: {pageSize: 5}},
                                            }}
                                            checkboxSelection
                                            onRowSelectionModelChange={handleSelectionChange}
                                            pageSizeOptions={[5, 10, 15]}
                                        />
                                        <div className="SubmitButton">
                                            <button onClick={deleteReport}>Delete Selected
                                                Reports{selectedRows.length > 1 && 's'} </button>
                                        </div>
                                    </div>
                                </div>
                            }

                        </header>
                    </>
                ) : (
                    <>
                        <p>
                            {"Not Authenticated"}
                        </p>
                    </>

                )
            }
        </main>

    );
}
export default LoadReport;
