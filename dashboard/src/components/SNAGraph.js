import {Button, Dropdown, Icon, Input, Popup} from "semantic-ui-react";
import {useEffect, useState} from "react";
import axios from "../api/axios";
import Plot from "react-plotly.js";
import {CommunitiesContent} from "./CommunitiesContent";
import {SNATrafficGraph} from "./SNATrafficGraph";

// SNAGraph component used to display scatter plot of network interactions based on retweet interactions.
export const SNAGraph = ({input_info, keywords, setDisableGeneralQuery, disableSNAGraphQueries, setCommunityWords, showSNAGraph, setShowSNAGraph}) => {

  const [nbCommunities, setNbCommunities] = useState("10");
  // Variables storing loading, disabling and error message states
  const [loading, setLoading] = useState(false)
  
  // Variable to store scatter plots returned by API upon request
  const [graphs, setGraphs] = useState(null);

  const [allKeywordsLabel, setAllKeywordsLabel] = useState(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")

  useEffect(() => {
    setAllKeywordsLabel(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")
  },[input_info]);

  // Dropdown menu options: keywords
  const dropKeywordsFilter = keywords.map((dictionaryKey) => {
    return {
      "key": dictionaryKey,
      "value": dictionaryKey,
      "text": dictionaryKey === "All"? allKeywordsLabel : dictionaryKey[0].toUpperCase()+dictionaryKey.slice(1)}
  });

  const [SNAcolors, setSNAcolors] = useState(null)
  // Variables storing filters to apply to scatter plot
  const [selectedKeywordsFilters, setSelectedKeywordsFilters] = useState(keywords[0]);
  const [noNetworkForTheseFilters, setNoNetworkForTheseFilters] = useState(false)

  const [sNATrafficGraphData, setSNATrafficGraphData] = useState(null);
  const [statesTable, setStatesTable] = useState(null);



  useEffect(() => {
    if (!(keywords.includes(selectedKeywordsFilters))){
      setSelectedKeywordsFilters(keywords[0]);
    }else {
      setSelectedKeywordsFilters(selectedKeywordsFilters);
    }
  },[showSNAGraph, keywords]);

  // useEffect hook to remove existing SNA scatter plot upon the generation of a new report
  useEffect(() => {
    var existingElement = document.getElementById('SNA');
    if (existingElement) {
      existingElement.innerHTML = '';
    }
    setNbCommunities(input_info === null? "10":input_info['nbCommunities'] === null || input_info['nbCommunities'] === undefined ? "10":input_info['nbCommunities'])
  },[keywords, showSNAGraph]);

  useEffect(() => {
    if (input_info?.claim === null) {
      setShowSNAGraph(false);
    }
  }, [input_info]);

  // useEffect hook to update the SNA scatter plot upon a change in the graph data or the keywords or
  // sentiment filters
  useEffect(() => {
    if (showSNAGraph) {
      if (graphs != null) {
        var existingElement = document.getElementById('SNA');
        if (existingElement) {
          existingElement.innerHTML = '';
        }

        if (graphs[selectedKeywordsFilters] !== undefined) {
          if (graphs[selectedKeywordsFilters] !== undefined && graphs[selectedKeywordsFilters] != null) {
            setNoNetworkForTheseFilters(false)
            window.Bokeh.embed.embed_item(graphs[selectedKeywordsFilters], 'SNA')
          } else {
            setNoNetworkForTheseFilters(true)
          }
        }
      }
    }
  },[graphs, selectedKeywordsFilters]);



  useEffect(() => {
    if (!keywords.includes(selectedKeywordsFilters)){
      setSelectedKeywordsFilters(keywords[0]);
    }
  },[keywords]);

  // Post query to API for Social Network Analysis (SNA) visualisation
  const getVisualisation = async () => {
    console.log("generate SNA visualisation")
    let nbCommunitiesInt = 0
    if (nbCommunities !== "") {
      nbCommunitiesInt = parseInt(nbCommunities)
    }
    let info_for_api = {
      "keyword": selectedKeywordsFilters,
      "keywords": input_info["keywords"].filter(keyword => keyword !== "All"),
      "date_start": input_info["date_start"],
      "date_end": input_info["date_end"],
      "limit": input_info["limit"],
      "source": input_info["source"],
      "operator": input_info["operator"],
      "random_seed": input_info["random_seed"],
      "language": input_info["language"],
      "sentiment": input_info["sentiment"],
      "location": input_info["location"],
      "location_type": input_info["location_type"],
      "nb_communities": nbCommunitiesInt,
    }

    console.log("INPUT INFO FOR SNA", info_for_api)

    const response = await axios.post('/api/social_network_analysis', {
      data: info_for_api,
      timeout: 30000
    });
    if (response.status === 200) {
      let data_resp = response.data
        console.log("SNA RESPONSE", data_resp)
        setGraphs(data_resp["sna_figure"])
        setStatesTable(data_resp["network_stats"])
        setSNATrafficGraphData(data_resp["communities_traffic"])
        setSNAcolors(data_resp["communities_colors"])
        setCommunityWords(data_resp["top_words"])
        setShowSNAGraph(true)
        setLoading(false)
    } else {
      setLoading(false)
      setShowSNAGraph(false)
    }
    setDisableGeneralQuery(false)
  }


  const renderSNAVis = () => {
    if (noNetworkForTheseFilters) {
      return (
          <div className="ErrorMessage">
            <p>There is no network information for this keyword.</p>
          </div>
      )
    } else {
      return (
          <div className={showSNAGraph ? 'SNAGraphVis' : 'hidden'}>
            <div id="SNA" className="bk-root"></div>
          </div>
      )
    }
  }


  const renderSNAController = () => {
    return (
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
            <h3 style={{marginRight: "5px"}}>Nb communities</h3>
            <Popup
              content="The number of communities determines the number of communities highlighted in the visualisation. By default the number of communities is 10, which means only the top 10 biggest communities for the current query will be colored. Once the Social Network Analysis graph is generated, you can go to the Wordcloud component to see the wordcloud obtained from each community's user descriptions by selecting 'Community user descriptions' under the 'Field' filter. "
              trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
            />
          </div>
          <Input
              placeholder="Nb topics (optional)..."
              type="number"
              min="1"
              step="1"
              // ref={nbTopicsRef}
              value={nbCommunities}
              onChange={(e, {value}) => {setNbCommunities(value);}}
              className="NbCommunitiesInput"
          />
        </div>
        <div>
          <div>
            <Button
                onClick={() => {
                  setDisableGeneralQuery(true)
                  setLoading(true)
                  getVisualisation()
                }}
                disabled={disableSNAGraphQueries}
                loading={loading}
                style={{marginRight: 50}}
            >Generate</Button>
          </div>
        </div>
      </div>)
  };

  return (
    <div className="Visualisation">
      <div className="MainTitleWithPopup">
        <h2>Social Network Analysis</h2>
        <Popup
          content="Clicking 'Generate' in this component will display authors for the current query such that users that retweet each other a lot are located close to each other. Once a visualisation is generated, hovering over a datapoint will display the user's screen name and description. Clicking on a datapoint will open the user profile on Twitter (X) in a new tab."
          trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
        />
      </div>
      <>
        {renderSNAController()}
        {showSNAGraph && (
          <>
            {renderSNAVis()}
            <SNATrafficGraph
              input_info={input_info}
              keywords={keywords}
              sNATrafficGraphData={sNATrafficGraphData}
              showSNAGraph={showSNAGraph}
              SNAcolors={SNAcolors}
            />
            <CommunitiesContent
              input_info={input_info}
              statesTable = {statesTable}
              keywords={keywords}
              showSNAGraph = {showSNAGraph}/>
          </>
        )}
      </>
    </div>
  );
};
export default SNAGraph;