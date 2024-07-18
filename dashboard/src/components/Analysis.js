import {useNavigate} from "react-router-dom";
import React, {useState, useEffect} from "react"
import axios from "../api/axios";
import useAuth from "../hooks/useAuth";

import {InputHeader} from './Input';
import {VolumesGraph} from './VolumesGraph';
import {SentimentGraph} from "./SentimentGraph"
import {LanguagesGraph} from "./LanguagesGraph"
import {MapGraph} from './MapGraph';
import {WordcloudGraph} from './WordcloudGraph';
import {TopContent} from "./TopContent";
import {TopicModelling} from "./TopicModelling";
import {Sticky} from "semantic-ui-react";
import 'semantic-ui-css/semantic.min.css'
import '../App.css';
import SNAGraph from './SNAGraph';


const ANALYSIS_URL = '/analysis';
const LOGIN_PAGE = '/login';


const queryParameters = new URLSearchParams(window.location.search)
const parameters = queryParameters.get("report")
let response = null
let consumed = false
let input_info = null

// Generating report from info stored in URL
//if (parameters !== null && (response === null || response.toString() === {})) {
if (parameters !== null) {
    console.log("Inside Analysis with parameters")
    input_info = JSON.parse(decodeURIComponent(parameters))
    console.log("input_info --> ", input_info)
    console.log(JSON.parse(decodeURIComponent(parameters)))

    response = await axios.post('/api/search', {
        data: input_info,
        timeout: 30000
    }).then(data => {
        console.log("response --> : ", data)
        return data;
    }).catch((error) => {
        console.log("Error --> : ", error)
        return null;
    });
}


const Analysis = () => {
    const emptyData = {
        "show_report": false,
        "hits": 0,
        "report": {}
    }

    const setAuth = useAuth();
    const navigate = useNavigate();
    const [savingButton, setSavingButton] = useState(false);

    useEffect(() => {
        const handleBackButton = () => {
            // Reload the page when the user presses the back button
            window.location.reload();
        };

        // Add event listener for the popstate event (back button)
        window.addEventListener('popstate', handleBackButton);

        // Clean up the event listener when the component unmounts
        return () => {
            window.removeEventListener('popstate', handleBackButton);
        };
    }, []);

    useEffect(() => {
        async function fetchData() {
            try {
                if (!(setAuth.accessToken)) {
                    console.log("Trying to logging in by auth!")
                    const res = await axios.get('/auth', {timeout: 15000});
                    //setResponse(res)
                    if (res.data.accessToken.toString() === "") {
                        throw new Error("Not authenticated");
                    }
                    setAuth.login(res?.data?.accessToken, res?.data?.username, res?.data?.userType)
                    console.log("logging in by auth Done!!")
                }
            } catch (err) {
                console.log(err)
                setAuth.logout(); // it seems that the logout cause by this
                navigate(LOGIN_PAGE, {state: {from: ANALYSIS_URL}});
            }
        }

        fetchData();
    }, [response]);

    console.log()
    const [data, setData] = useState(emptyData)
    const [inputInfo, setInputInfo] = useState(input_info)
    const [topicWords, setTopicWords] = useState(null)
    const [communityWords, setCommunityWords] = useState(null)
    const [disableGeneralQuery, setDisableGeneralQuery] = useState(false)
    const [disableTopicModellingQueries, setDisableTopicModellingQueries] = useState(false)
    const [disableSNAGraphQueries, setDisableSNAGraphQueries] = useState(false)

    const [showSNAGraph, setShowSNAGraph] = useState(false)

    const [showSummary, setShowSummary] = useState(false)
    const [nbHits, setNbHits] = useState(null)
    const [keywordsList, setKeywordsList] = useState(null)

    // Setting useState variables to cached info if response is not null (i.e. generated from cache)
    if (response !== null && consumed === false) {
        console.log("Response consumed!")
        consumed = true;
        if (response.status === 200) {
            let data_resp = response.data
            let keywords = data_resp.keywords
            if (keywords.length === 2) {
                keywords = keywords.filter(function (key) {
                    return key !== 'All';
                });
            }
            input_info["keywords"] = keywords
            setData(data_resp);
            setInputInfo(input_info);
            setKeywordsList(Object.keys(data_resp.report))
            setNbHits(Object.fromEntries(Object.keys(data_resp.report).map(key => [key, data_resp.report[key].count])));
            setShowSNAGraph(false)
            setSavingButton(false)
            //window.history.pushState({}, document.title, "/analysis");
            //}))
        }
    }

    // Function to display or hide the summary of the current query when scrolling over the page
    const listenToScroll = () => {
        let heightToHideFrom = 600;
        const winScroll = document.body.scrollTop ||
            document.documentElement.scrollTop;

        if (winScroll > heightToHideFrom) {
            setShowSummary(true);
        } else {
            setShowSummary(false);
        }
    };

    // useEffect to add even listener to scroll upon first loading the page
    useEffect(() => {
        window.addEventListener("scroll", listenToScroll);
        return () =>
            window.removeEventListener("scroll", listenToScroll);
    }, [])


    // Render function for sticky summary (displayed at the top of the page when scrolling down on report)
    const renderSummary = () => {

        if (showSummary) {
            let keywordsSub = inputInfo["keywords"].filter(function (key) {
                return key !== 'All';
            })
            let keywordsStr = keywordsSub.join(", ")
            return (
                <div className="SummaryContainer">
                    <div className="SummaryItem">
                        <p><b>Dataset</b>: {inputInfo["source_text"]}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>Keywords</b>: {keywordsStr}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>Start date</b>: {inputInfo["date_start"]}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>End date</b>: {inputInfo["date_end"]}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>Language</b>: {inputInfo["language"]}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>Sentiment</b>: {inputInfo["sentiment"]}</p>
                    </div>
                    <div>
                        <p className="SummaryItem"><b>Country</b>: {inputInfo["location"]}</p>
                    </div>
                </div>
            )
        } else {
            return (
                <div className="SummaryContainer"/>
            )
        }
    }

    // Function to render every component in the report
    const renderReport = () => {
        if (data.show_report) {
            if (data.hits > 0) {
                console.log(data)
                return (
                    <div>
                        <Sticky className={showSummary ? 'StickySummary' : 'EmptySummaryContainer'}>
                            {renderSummary()}
                        </Sticky>
                        <div className="PageBody">
                            <VolumesGraph data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
                            <SentimentGraph data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
                            <LanguagesGraph data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
                            <MapGraph data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
                            <TopContent data={data.report} keywords={keywordsList} inputInfo={inputInfo}/>
                            <WordcloudGraph
                                data={data.report}
                                keywords={keywordsList}
                                topics={topicWords}
                                inputInfo={inputInfo}
                                communities={communityWords}
                            />
                            <TopicModelling
                                hits={nbHits}
                                input_info={inputInfo}
                                keywords={keywordsList}
                                setTopicWords={setTopicWords}
                                setDisableGeneralQuery={setDisableGeneralQuery}
                                disableTopicModellingQueries={disableTopicModellingQueries}
                                setInput={setInputInfo}
                            />
                            <SNAGraph
                                input_info={inputInfo}
                                keywords={keywordsList}
                                setDisableGeneralQuery={setDisableGeneralQuery}
                                disableSNAGraphQueries={disableSNAGraphQueries}
                                dataSource={data.dataSource}
                                operator={data.operator}
                                source_text={data.source_text}
                                setCommunityWords={setCommunityWords}
                                showSNAGraph={showSNAGraph}
                                setShowSNAGraph={setShowSNAGraph}
                            />
                        </div>
                    </div>
                )
            } else {
                return (
                    <div className="PageBody">
                        <div className="ErrorMessage">
                            <p>No tweets were found for these criteria.</p>
                        </div>
                    </div>
                )
            }
        }
    }

    return (
        <main className="App">
            {
                setAuth.accessToken ? (
                    <>
                        <div className="App">
                            <InputHeader
                                inputInfo={inputInfo}
                                setData={setData}
                                setInput={setInputInfo}
                                setNbHits={setNbHits}
                                setKeywordsList={setKeywordsList}
                                setDisableTopicModellingQueries={setDisableTopicModellingQueries}
                                setDisableSNAGraphQueries={setDisableSNAGraphQueries}
                                disableGeneralQuery={disableGeneralQuery}
                                savingButton={savingButton}
                                setSavingButton={setSavingButton}
                                setShowSNAGraph={setShowSNAGraph}
                            />
                            {renderReport()}
                        </div>
                    </>
                ) : (
                    <>
                        <p>
                            {"Logged out!"}
                            <br></br>
                            <a href="/login">{"Go to login...!"}</a>
                        </p>
                    </>
                )}


        </main>
    )

}
export default Analysis