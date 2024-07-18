// import { React } from "react";
import { DataGrid } from '@mui/x-data-grid';
import {useEffect, useState} from "react";
import {Dropdown, Icon, Popup} from "semantic-ui-react";


export const CommunitiesContent = ({input_info, statesTable, showSNAGraph, keywords}) => {

  const [allKeywordsLabel, setAllKeywordsLabel] = useState(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")

  useEffect(() => {
    setAllKeywordsLabel(input_info["operator"] === "AND" ? "All keywords" : "Any keyword")
  },[input_info]);

  // Keyword filter
  const [dropKeywordsFilter, setDropKeywordsFilter] = useState(keywords.map((dictionaryKey) => {
    return {
      "key": dictionaryKey,
      "value": dictionaryKey,
      "text": dictionaryKey === "All"? allKeywordsLabel : dictionaryKey[0].toUpperCase()+dictionaryKey.slice(1)}
  }));

  const TOP_N = 10

  const [selectedKeywordsFilter, setSelectedKeywordsFilter] = useState(keywords[0]);
  // const [selectedSentimentFilter, setSelectedSentimentFilter] = useState('All Sentiments');

  const replaceTextWithURL = (params, field, template) => {
    const parts = params.row[field].slice(0, TOP_N)
    return (
      <p>
        {parts.map((part, index) => {
          return (
            <span>
              <a key={part} href={template.replace("@", part)} target="_blank">{part}</a>
              {index !== parts.length - 1 && ", "}
            </span>
          )
        })}
      </p>
    )
  }

  const roundNumber = (params, field) => {
    return (Math.round(params.row[field] * 100) / 100)
  }

  // var formatData = (keyword, sentiment) => {
  var formatData = (keyword) => {
    let heightType = "auto"
    let rows = []
    if (statesTable !== undefined && statesTable !== null){
      if (statesTable[keyword] !== null && statesTable[keyword] !== undefined){
        if (statesTable[keyword] !== null && statesTable[keyword] !== undefined){
          rows = statesTable[keyword]
        }
      }
    }

    let columns = [
      { 
        field: 'Community',
        width: 100,
        headerAlign: 'center',
        align: 'center',
        renderHeader: () => (<strong>Community</strong>),
      },
      {
        field: 'Nb active accounts',
        width: 100,
        align: "center",
        headerAlign: 'center',
        renderHeader: () => (<strong>Nb accounts</strong>),
      },
      {
        field: 'Nb tweets per account',
        width: 150,
        align: "center",
        headerAlign: 'center',
        renderHeader: () => (<strong>Nb tweets per account</strong>),
        renderCell: (params) => roundNumber(params, 'Nb tweets per account')
      },
      {
        field: 'Nb retweets per tweet',
        width: 150,
        headerAlign: 'center',
        align: 'center',
        renderHeader: () => (<strong>Nb retweets per tweet</strong>),
        renderCell: (params) => roundNumber(params, 'Nb retweets per tweet')
      },
      {
        field: 'Top 20 most retweeted accounts',
        width: 300,
        headerAlign: 'center',
        align: 'center',
        renderHeader: () => (<strong>Top {TOP_N} accounts</strong>),
        renderCell: (params) => replaceTextWithURL(params,'Top 20 most retweeted accounts', "https://twitter.com/@")
      },
    ];
    return {"rows": rows, "columns": columns, "heightType": heightType};
  };
  // const [dataGridConfig, setDataGridConfig] = useState(formatData(selectedKeywordsFilter, selectedSentimentFilter));
  const [dataGridConfig, setDataGridConfig] = useState(formatData(selectedKeywordsFilter));

  const title = "Communities Stats"

  useEffect(() => {
    setDropKeywordsFilter(keywords.map((dictionaryKey) => {
      return {
        "key": dictionaryKey,
        "value": dictionaryKey,
        "text": dictionaryKey === "All"? allKeywordsLabel : dictionaryKey[0].toUpperCase()+dictionaryKey.slice(1)}
    }))
    setSelectedKeywordsFilter(keywords[0])
  },[keywords]);


  useEffect(() => {
    if (showSNAGraph){
      if (statesTable !== undefined && statesTable !== null){
        if (statesTable[selectedKeywordsFilter] !== undefined && statesTable[selectedKeywordsFilter] != null){
          if (statesTable[selectedKeywordsFilter] !== undefined && statesTable[selectedKeywordsFilter] != null){
            setDataGridConfig(formatData(selectedKeywordsFilter))
          }
        }
      }
    }
  }, [statesTable, showSNAGraph, selectedKeywordsFilter]);
  
  
  //if (showSNAGraph && dataGridConfig.rows !== null && dataGridConfig.rows !== undefined){
  return (
      showSNAGraph && dataGridConfig.rows !== null && dataGridConfig.rows !== undefined?(
        <div className="Visualisation">
          <div className="MainTitleWithPopup">
            <h2 style={{marginRight: "5px"}}>{title}</h2>
            <Popup
              content="This component shows statistics for each community. These include the number of accounts in the community for the current query, the average number of tweets per account, the average number of retweets per tweet and the screen name of the 10 most retweeted accounts in the community. Clicking on a user screen name will open the user profile on Twitter (X) in a new tab."
              trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
            />
          </div>
          <div className="DropDownGroup">
            <div className="DropDownMaps">
              <div className="SubTitleWithPopup">
                <h3 className="DropDownTitle">Keyword</h3>
                <Popup
                  content="If more than 1 keyword was provided, you can use the 'Keyword' filter to display results for each keyword independently, as well as for all keywords together ('All keywords')."
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
                  value={selectedKeywordsFilter}
                  onChange={(e, { value }) => setSelectedKeywordsFilter(value)}
                  closeOnChange={true}
                  name='tokensFiltersTypeDropdown'
                  id='tokensFiltersTypeDropdown'
                ></Dropdown>
              </div>
            </div>
          </div>
          <div className="TopContent" >
            <DataGrid
              getRowHeight={() => dataGridConfig["heightType"]}
              rows={dataGridConfig["rows"]}
              columns={dataGridConfig["columns"]}
              initialState={{
                ...dataGridConfig["rows"].initialState,
                pagination: { paginationModel: { pageSize: 5 } },
              }}
              pageSizeOptions={[5, 10, 15]}
              disableColumnSelector={true}
            />
          </div>
        </div>):
          null
      );
};