import React, { Component } from 'react';
import { ServiceUrl } from '../../config.js'
import waitFace from '../../assets/waitFace.png'
import {
  Button,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  Col,
  FormGroup,
  Input,
  Label,
  Row,
  Form,
  Badge, Pagination, PaginationItem, PaginationLink, Table 
} from 'reactstrap';
import axios from 'axios';

class AddData extends Component {
  constructor(props) {
    super(props);

    this.AiFace = this.AiFace.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.account = 0
    this.state = {
      faceimage: "",
      file:null,
      showData:[]
    };
  }

  handleChange = (e) => {
    const name = e.target.name;
    const value = e.target.value;
    let info = Object.assign({}, this.props);
    if (name.indexOf(".") != -1) {
      var arr = name.split(".")
      if (arr[1].indexOf("faceimage") != -1) {
        var img = e.target.files[0]
        var reader = new FileReader();

        if (!img) {
          console.log("failed")
          this.setState({
            show_addimage: false,
          });
        }
        else {
          console.log("success")
          reader.readAsDataURL(img);
          reader.onload = function (e) {
            var faceArr = e.target.result.split(",")
            this.setState({
              faceimage: faceArr[1],
              show_addimage: true,
              file:img
            });
            // console.log(e.target.files[0])
            // var temp1 = info[arr[0]]
            // temp1[arr[1]] = this.state.faceimage
          }.bind(this)
          e.target.value = ''
        }
      }
      else {
        var temp1 = info[arr[0]]
        temp1[arr[1]] = value
      }
    }
    else {
      info[name] = value;
    }
  }

  AiFace(){
    var formdata1=new FormData();
    formdata1.append('image',this.state.file,this.state.file.name);
    axios.post( `${ServiceUrl}/faceIdentity`,
    formdata1,
    {
      headers: {
        'Content-Type':'application/x-www-form-urlencoded',
        "Access-Control-Allow-Origin": "*",
        'Accept': 'application/json'
      },
    }
    ).then(resp => {
        this.setState({
          showData:resp.data
        },console.log(this.state.showData))
  })
  }

  render() {
    return (
      <div className="animated fadeIn">
        <Row >
        <Col xs="12" lg="9">
            <Card>
              <CardHeader>
                <i className="fa fa-align-justify"></i> 考勤信息
              </CardHeader>
              <CardBody>
                <Table responsive>
                  <thead>
                  <tr>
                    <th>头像</th>
                    <th>姓名</th>
                    <th>工号</th>
                    {/* <th>考勤记录</th> */}
                  </tr>
                  </thead>
                  <tbody>
                  {
                    this.state.showData.map(function (each, idx) {
                      console.log(each)
                      return(
                        <tr key={idx}>
                          <td>
                          <img height="60px" width="60px" src={each["imgPath"]}></img>
                          </td>
                          <td >{each["name"]}</td>
                          <td >{each["score"]}</td>
                          {/* // <td >{each[2]}</td> */}
                        </tr>
                      )
                    })
                  }
                  </tbody>
                </Table>
              </CardBody>
            </Card>
          </Col>

          <Col xs="12" sm="6" lg="3">
            <Card>
              <CardHeader>
                <strong>人脸上传</strong>
              </CardHeader>
              <CardBody>
                <FormGroup>
                  <Label htmlFor="QQ">人脸图片</Label>

                  <div className="p-2">
                    <div className="d-flex flex-column justify-content-start align-items-left" >
                      <div className="p-2">
                        <img  src={waitFace} height="260" border="" alt="" hidden={this.state.faceimage!=""}></img>
                        <img  src={'data:image/jpeg;base64,' + this.state.faceimage} height="260"  border="" alt=""></img>
                      </div>

                      <div className="p-1">
                        {/* <FormGroup hidden={!this.state.faceimage == "" || !attributes.faceimage == ""}>
                          <Form id="imgForm">
                            <input type="file"
                              title="人脸图"
                              size="sm"
                              display="none"
                              name="attributes.faceimage"
                              accept="image/jpeg,image/jpg,image/png"
                              onChange={this.handleChange} />
                          </Form>
                        </FormGroup> */}
                      </div>
                    </div>
                  </div>
                  {/* <img  width="150" border="" alt=""></img> */}
                  {/* <Input type="file" id="userInfo" onChange={event => (this.user_id =event.target.value)} placeholder="刘XX" /> */}
                      
                <Form id="imgForm">
                  <input type="file"
                    id="upload_file"
                    title="人脸图"
                    size="sm"
                    display="none"
                    name="attributes.faceimage"
                    accept="image/jpeg,image/jpg,image/png"
                    onChange={this.handleChange} />
                </Form>

                </FormGroup>
              </CardBody>
              <CardFooter>
                <span style={{ marginLeft: '12rem' }}></span>
                <Button type="submit" size="sm" onClick={this.AiFace} color="danger">人脸考勤</Button>
              </CardFooter>
            </Card>
          </Col>

        </Row>
      </div>
    );
  }
}

export default AddData;
