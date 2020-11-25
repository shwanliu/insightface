// 服务器地址的配置在这里
var ServiceUrl = 'http://localhost:5001'
function UpdateServiceUrl(newUrl) {
    ServiceUrl = newUrl
    console.log("UpdateServiceUrl has been updated to " + ServiceUrl);
}
console.log("Connected to " + ServiceUrl + " ...");
export { ServiceUrl, UpdateServiceUrl};
