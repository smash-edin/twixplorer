import axios from "axios";

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

axios.defaults.baseURL = 'http://127.0.0.1:5000'
// NOTE: If Flask backend runs on a different machine from React front-end, add URL to Flask back-end with port number
// 5000 in place of this URL (e.g. http://myserver:5000)

export default axios.create({
    baseURL: 'http://127.0.0.1:5000', //Placeholder, add IP address of machine running Flask back-end with port number 5000
    withCredentials: true,
    crossOrigin: true,
});
