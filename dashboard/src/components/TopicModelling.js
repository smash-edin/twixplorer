import {Button, Dropdown, Icon, Input, Popup} from "semantic-ui-react";
import {useEffect, useState} from "react";
import axios from "../api/axios";

// TopicModelling component used to display scatter plot of tweets based on 2D embeddings, to cluster tweets and to
// find location of tweets matching a given claim
export const TopicModelling = ({
                                   hits,
                                   input_info,
                                   keywords,
                                   setTopicWords,
                                   setDisableGeneralQuery,
                                   disableTopicModellingQueries,
                                   setInput
                               }) => {

    const random_seed = (input_info === null || input_info === undefined) ? 42 : (input_info["random_seed"] === null) ? 42 : JSON.stringify(input_info['random_seed'])

    // Variables storing optional user inputs (number of topics for clustering and claim)
    const [nbTopics, setNbTopics] = useState(0);
    const [claim, setClaim] = useState("");

    // Variables storing loading, disabling and error message states
    const [loading, setLoading] = useState(false)
    const [showTopicModelling, setShowTopicModelling] = useState(false)
    const [noTweetsForTheseFilters, setNoTweetsForTheseFilters] = useState(false)

    // Variables storing filters to apply to scatter plot
    const [selectedKeywordsFilters, setSelectedKeywordsFilters] = useState(keywords[0]);

    // Variable to store scatter plots returned by API upon request
    const [graphs, setGraphs] = useState(null);

    const [allKeywordsLabel, setAllKeywordsLabel] = useState(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")

    useEffect(() => {
        setAllKeywordsLabel(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")
    }, [input_info]);

    // Dropdown menu options: keywords
    const dropKeywordsFilter = keywords.map((dictionaryKey) => {
        return {
            "key": dictionaryKey,
            "value": dictionaryKey,
            "text": dictionaryKey === "All" ? allKeywordsLabel : dictionaryKey[0].toUpperCase() + dictionaryKey.slice(1)
        }
    });

    const [dropSelectedSentiments, setDropSelectedSentiments] = useState([])
    const [sentimentDisable, setSentimentDisable] = useState(false)
    const [selectedSentiment, setSelectedSentiment] = useState('All Sentiments');


    useEffect(() => {
        if (input_info["sentiment"] === "All") {
            setDropSelectedSentiments([
                {key: 'All Sentiments', text: 'All Sentiments', value: 'All Sentiments',},
                {key: 'Positive', text: 'Positive', value: 'Positive',},
                {key: 'Neutral', text: 'Neutral', value: 'Neutral',},
                {key: 'Negative', text: 'Negative', value: 'Negative',},
            ])
        } else {
            setDropSelectedSentiments([
                {key: input_info["sentiment"], text: input_info["sentiment"], value: input_info["sentiment"]}
            ])
        }
        setSentimentDisable(input_info["sentiment"] !== "All")
        setSelectedSentiment(input_info["sentiment"] === 'All' ? 'All Sentiments' : input_info["sentiment"])
        console.log("Topic Modelling : ", input_info)
    }, [hits, input_info, keywords])

    // useEffect hook to remove existing TopicModelling scatter plot upon the generation of a new report
    useEffect(() => {
        var existingElement = document.getElementById('topic_mod');
        if (existingElement) {
            existingElement.innerHTML = '';
        }
        setShowTopicModelling(false)
        setTopicWords(null)
        setNbTopics(input_info === null ? "" : input_info['nbTopics'] === null || input_info['nbTopics'] === undefined ? "" : input_info['nbTopics'])
        setClaim(input_info === null ? "" : input_info['claim'] === null || input_info['claim'] === undefined ? "" : input_info['claim'])
        if (!keywords.includes(selectedKeywordsFilters)) {
            setSelectedKeywordsFilters(keywords[0]);
        }
    }, [hits, keywords]);

    // useEffect hook to update the topic modelling scatter plot upon a change in the graph data or the keywords or
    // sentiment filters
    useEffect(() => {
        if (showTopicModelling) {
            if (graphs != null) {
                var existingElement = document.getElementById('topic_mod');
                if (existingElement) {
                    existingElement.innerHTML = '';
                }
                if (graphs[selectedKeywordsFilters] !== undefined) {
                    if (graphs[selectedKeywordsFilters][selectedSentiment] !== undefined && graphs[selectedKeywordsFilters][selectedSentiment] != null) {
                        setNoTweetsForTheseFilters(false)
                        window.Bokeh.embed.embed_item(graphs[selectedKeywordsFilters][selectedSentiment], 'topic_mod')
                    } else {
                        setNoTweetsForTheseFilters(true)
                    }
                }
            }
        }
    }, [graphs, selectedSentiment, selectedKeywordsFilters]);

    // Post query to API for TopicModelling visualisation
    const getVisualisation = async () => {
        console.log("generate topic modelling visualisation")
        console.log("random_seed @ Topic Modelling: ----====> " + random_seed)
        let nbTopicsInt = 0
        if (nbTopics !== "") {
            nbTopicsInt = parseInt(nbTopics)
        }
        let info_for_api = {
            "keywords": input_info["keywords"],
            "date_start": input_info["date_start"],
            "date_end": input_info["date_end"],
            //"limit": input_info["limit"],
            "limit": 100000,
            "source": input_info["source"],
            "operator": input_info["operator"],
            "random_seed": input_info["random_seed"],
            "nb_topics": nbTopicsInt,
            "claim": claim,
            "language": input_info["language"],
            "sentiment": input_info["sentiment"],
            "location": input_info["location"],
            "location_type": input_info["location_type"],
        }
        console.log("Info being sent to backend is:", info_for_api)

        const response = await axios.post('/api/topic_modelling', {
            data: info_for_api,
            timeout: 30000
        }).catch((error) => {
            if (error?.response?.status === 401) {
                window.open('/login')
            } else {
                alert("Something went wrong, please try again.")
            }
        });
        if (response !== undefined) {
            if (response.status === 200) {
                let data_resp = response.data
                console.log("TOPIC MODELLING RESPONSE")
                console.log(data_resp)
                setGraphs(data_resp["figures"])
                setTopicWords(data_resp["top_words"])
                setShowTopicModelling(true)
                setLoading(false)
            } else {
                console.log("responses didnt work")
                setTopicWords(null)
                setLoading(false)
            }
        } else {
            console.log("responses didnt work")
            setTopicWords(null)
            setLoading(false)
        }
        setDisableGeneralQuery(false)
    }

    // Function to render message about volume matching query
    const renderVolumeMessage = () => {
        if (hits[selectedKeywordsFilters] !== undefined) {
            if (hits[selectedKeywordsFilters] > 100000) {
                return (
                    <div className="CappingWarningDisplay">
                        <p className="CappingWarning">
                            <b>{hits[selectedKeywordsFilters].toLocaleString()}</b> tweets were found in total. To
                            enable the topic discovery to run in reasonable time, only <b>100K</b> randomly sampled
                            tweets will be used.
                        </p>
                    </div>
                )
            } else {
                return (
                    <div className="CappingWarningDisplay">
                        <p className="CappingWarning">
                            <b>{hits[selectedKeywordsFilters].toLocaleString()}</b> tweets were found.
                        </p>
                    </div>
                )
            }
        }
    }

    // Function to display either the topic modelling Bokeh scatter plot, or an error message if the tweet volume for the
    // given filters is zero
    const renderTopicModVis = () => {
        if (noTweetsForTheseFilters) {
            return (
                <div className="ErrorMessage">
                    <p>There are no tweets for this keyword and sentiment.</p>
                </div>
            )
        } else {
            return (
                <div className={showTopicModelling ? 'TopicModellingVis' : 'hidden'}>
                    <div id="topic_mod" className="bk-root"></div>
                </div>
            )
        }
    }

    // Render code for the TopicModelling component
    return (
        <div className="Visualisation">
            <div className="MainTitleWithPopup">
                <h2 style={{marginRight: "5px"}}>Topic Discovery</h2>
                <Popup
                    content="Clicking 'Generate' in this component will display the tweets in the current query in 'semantic space': i.e. tweets that are semantically similar are located close to each other. The number of results is capped at 100,000 (tweets are randomly sample if the volume exceeds this threshold). Once a visualisation is generated, hovering over a datapoint will display the tweet. Clicking on a datapoint will open the tweet on Twitter in a new tab."
                    trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                />
            </div>
            <div className="ClusterGenerate">
                <div className="SubTitleWithPopup">
                    <h3 style={{marginRight: "5px"}}>Nb topics</h3>
                    <Popup
                        content="Specifying a number of topics greater than zero before generating will enable the clustering the tweets into this given number of topics, visually signified with different colors. You can then see a wordcloud of each topic using the 'Wordcloud' component above by selecting 'Topics' under the 'Field' filter. "
                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                    />
                </div>
                <Input
                    placeholder="optional"
                    type="number"
                    min="0"
                    step="1"
                    // ref={nbTopicsRef}
                    value={nbTopics}

                    onChange={(e, {value}) => {
                        setNbTopics(value);
                        //setInput({ ...input_info, "nbTopics": value ===""? "":parseInt(value)})
                    }
                    }
                    className="NbTopicsInput"
                />

                <div className="SubTitleWithPopup">
                    <h3 style={{marginRight: "5px"}}>Claim</h3>
                    <Popup
                        content="Specifying a claim will flag up the location (shown as a large black dot) of tweets similar to the claim in the visualisation. "
                        trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                    />
                </div>
                <Input
                    placeholder="optional"
                    type="text"
                    value={claim}
                    onChange={(e, {value}) => {
                        setClaim(value);
                        //setInput({ ...input_info, "claim": value})
                    }
                    }

                    className="ClaimInput"
                />

                <Button
                    onClick={() => {
                        setDisableGeneralQuery(true)
                        setLoading(true)
                        setInput({...input_info, "claim": claim, "nbTopics": nbTopics})
                        getVisualisation()
                    }}
                    disabled={disableTopicModellingQueries}
                    loading={loading}
                    style={{marginRight: 50}}
                >Generate</Button>

            </div>
            <div className="DropDownGroup">
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 style={{marginRight: "5px"}}>Keywords</h3>
                        <Popup
                            content="Once the visualisation is generated, if more than 1 keyword was provided, you can use the 'Keyword' filter to display results for each keyword independently, as well as for all keywords together ('All keywords')."
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <div className="DropDownMenu">
                        <Dropdown
                            label='TokensKeywordsFilter'
                            fluid
                            selection
                            options={dropKeywordsFilter}
                            text={dropKeywordsFilter.text}
                            floating
                            labeled={true}
                            className='source'
                            icon={null}
                            value={selectedKeywordsFilters}
                            onChange={(e, {value}) => setSelectedKeywordsFilters(value)}
                            closeOnChange={true}
                            name='tokensFiltersTypeDropdown'
                            id='tokensFiltersTypeDropdown'
                        ></Dropdown>
                    </div>
                </div>
                <div className="DropDownMaps">
                    <div className="SubTitleWithPopup">
                        <h3 style={{marginRight: "5px"}}>Tweet's sentiment</h3>
                        <Popup
                            content="Once the visualisation is generated, use the Tweet's sentiment filter to filter the results shown by sentiment."
                            trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
                        />
                    </div>
                    <div className="DropDownMenu">
                        <Dropdown
                            label='tokensFilter'
                            fluid
                            selection
                            disabled={sentimentDisable}
                            options={dropSelectedSentiments}
                            text={dropSelectedSentiments.text}
                            floating
                            labeled={true}
                            className='source'
                            icon={null}
                            value={selectedSentiment}
                            onChange={(e, {value}) => setSelectedSentiment(value)}
                            closeOnChange={true}
                            name='tokensFiltersTypeDropdown'
                            id='tokensFiltersTypeDropdown'
                        ></Dropdown>
                    </div>
                </div>
            </div>
            {renderVolumeMessage()}
            {renderTopicModVis()}
        </div>
    );
};