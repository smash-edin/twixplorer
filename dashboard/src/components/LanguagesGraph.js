import Plot from "react-plotly.js";
import {Dropdown, Icon, Popup} from "semantic-ui-react";
import {useEffect, useState} from "react";

// LanguagesGraph component used to display the prevalence of different languages in the data
export const LanguagesGraph = ({data, keywords, inputInfo}) => {

  // Function to obtain the mapping from an index to a color from specified colormap
  const getRandomColor = (index) => {
    const colors = [
      'rgb(31, 119, 180)',
      'rgb(255, 127, 14)',
      'rgb(44, 160, 44)',
      'rgb(214, 39, 40)',
      'rgb(148, 103, 189)',
    ];
    return colors[index % colors.length];
  };

  const [allKeywordsLabel, setAllKeywordsLabel] = useState(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")

  useEffect(() => {
    setAllKeywordsLabel(inputInfo["operator"] === "AND" ? "All keywords" : "Any keyword")
  },[inputInfo]);

  // Variable storing all the keywords to be displayed in a dropdown menu (used to filter language per keyword)
  const dropKeywordsFilter = Object.keys(data).map((dictionaryKey) => {
    return {
      "key": dictionaryKey,
      "value": dictionaryKey,
      "text": dictionaryKey === "All"? allKeywordsLabel : dictionaryKey[0].toUpperCase()+dictionaryKey.slice(1)}
  });

  // Local variable to store the keyword filter currently selected by the user
  const [selectedKeywordFilter, setSelectedKeywordFilter] = useState(keywords[0]);
  const [selectedLanguageData, setSelectedLanguageData] = useState(data[selectedKeywordFilter]);
  const [languageFigureConfig, setLanguageFigureConfig] = useState({});

  // Variable to store information for language plot (initialised with empty skeleton)
  const [layout, setLayout] = useState({
    //title: plot_title,
    xaxis: { title: 'Date' },
    yaxis: { title: 'Count' },
    barmode: 'stack',
    modebar: {remove: ['lasso2d', 'select2d', "autoscale", "zoomIn2d", "zoomOut2d"]},
  })

  // useEffect hook to update the selected language data to display upon a change in the keyword filter or in the data
  // passed by the parent component (i.e. TestPage)
  useEffect(() => {
    if (selectedKeywordFilter in data){
      setSelectedLanguageData(data[selectedKeywordFilter])
    }else{
      setSelectedKeywordFilter(keywords[0])
      setSelectedLanguageData(data[keywords[0]])
    }
  },[data, keywords, selectedKeywordFilter]);

  // useEffect hook to update the language plot information upon a change in the selected data or in the data passed by
  // the parent component (i.e. TestPage)
  useEffect(() => {
    let items = selectedLanguageData["Languages_Distributions"]
    let title = "Languages Distribution"
    let key1 = "Language"
    let key2 = "Count"

    const x = items.map(items => items[key1]);
    const y = items.map(items => items[key2]);

    let color = getRandomColor(x)
    
    const traces =  [{
      x,
      y,
      type: 'bar',
      labels: {'language': "Language", key1: key1, 'count': "Count", 'english': 'English'},
      marker: {  color: color },
    }];

    setLanguageFigureConfig({'data': traces, 'title': title, 'key1': key1, 'key2': key2 })
    setLayout({
      xaxis: { title: languageFigureConfig['key1'] },
      yaxis: { title: languageFigureConfig['key2'] },
      barmode: 'stack',
      modebar: {remove: ['lasso2d', 'select2d', "autoscale", "zoomIn2d", "zoomOut2d"]},
    })
  }, [data, keywords, selectedLanguageData]);

  // Render code for the LanguageGraph component
  return (
    <div className="Visualisation">
      <div className="MainTitleWithPopup">
        <h2 style={{marginRight: "5px"}}>{languageFigureConfig['title']}</h2>
        <Popup
          content="This component shows the volume of data per language. You can click on a specific bar to generate a new report (in a new tab) for the subset of the current data that corresponds to this specific keyword and language. Note that if the dataset only contains one language, a single bar will be shown in the graph."
          trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
        />
      </div>
      <div  className="DropDownGroup">
        <div className="DropDownMaps">
          <div className="SubTitleWithPopup">
            <h3 className="DropDownTitle">Keyword</h3>
            <Popup
              content="If more than 1 keyword was provided, you can use the 'Keyword' filter to display results for each keyword independently, as well as for all keywords together ('Any keyword'/'All keywords')."
              trigger={<div className='InfoIcon'><Icon name='question circle' size="small"/></div>}
            />
          </div>

          <div className="DropDownMenu">
            <Dropdown
              label='Keyword'
              fluid
              selection
              options={dropKeywordsFilter}
              text={dropKeywordsFilter.text}
              floating
              labeled={true}
              icon={null}
              value={selectedKeywordFilter}
              onChange={(e, { value }) => setSelectedKeywordFilter(value)}
              closeOnChange={true}
              name='filtersTypeDropdown'
              id='filtersTypeDropdown'
            ></Dropdown>
          </div>
        </div>
      </div>
      <div>
        <Plot
          data={languageFigureConfig['data']}
          layout={layout}
          onClick={function(event){
              console.log(event)
              const relKeyword = selectedKeywordFilter === "All" ? keywords.filter(function (key) { return key !== 'All'; }).join(",") : selectedKeywordFilter
              const generate_report = window.confirm("A new report will be generated with the following filters:" +
                  "\n Keywords:"+ relKeyword +
                  "\n Dataset:"+ inputInfo["source_text"] +
                  "\n Operator:"+ inputInfo["operator"] +
                  (inputInfo["date_start"] + " to " + inputInfo["date_end"]!== " to "? "\t dates :" + inputInfo["date_start"] + " to " + inputInfo["date_end"]: "") +
                  "\n Sentiment:"+ inputInfo["sentiment"] +
                  "\n Language:"+ event.points[0].x +
                  "\n Location of "+ (inputInfo["location_type"] === 'author'? 'users':'tweets') + ": " + inputInfo["location"] +
                  "\n\n Do you want to continue?");
              if (generate_report !== false && generate_report !== null){
                  const page_path = window.location.pathname + "?report="
                  window.open(page_path+encodeURIComponent(
              JSON.stringify(
                {
                  "keywords": relKeyword,
                  "source": inputInfo["source"],
                  "source_text": inputInfo["source_text"],
                  "operator": inputInfo["operator"],
                  limit: 250,
                  "date_start": inputInfo["date_start"],
                  "date_end": inputInfo["date_end"],
                  "sentiment": inputInfo["sentiment"],
                  "language": event.points[0].x,
                  "location": inputInfo["location"],
                  "location_type": inputInfo["location_type"],
                })),
              "_blank")};
              }
            }
        />
      </div>
    </div>
  );
};