import React, { Component } from 'react';
import { ServiceUrl } from '../../config.js'
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
  Badge, Pagination, PaginationItem, PaginationLink, Table 
} from 'reactstrap';
import axios from 'axios';

class Search extends Component {
  constructor(props) {
    super(props);

    this.toggle = this.toggle.bind(this);
    this.toggleFade = this.toggleFade.bind(this);
    this.searchDate = this.searchDate.bind(this);
    this.user_id = "001"
    this.s_time1 = "2019-12-06"
    this.s_time2 = "0000"
    this.e_time1 = "2019-12-06"
    this.e_time2 = "0000"
    this.att_nums = 61
    this.state = {
      collapse: true,
      fadeIn: true,
      timeout: 300,
      showData:[]
    };
  }

  toggle() {
    this.setState({collapse: !this.state.collapse });
  }

  toggleFade() {
    this.setState((prevState) => { return { fadeIn: !prevState }});
  }

  searchDate(){
    var reg1 = new RegExp( '-' , "g" )
    var reg2 = new RegExp( ':' , "g" )
    console.log(this.s_time1.toString().replace(reg1,"")+this.s_time2.toString().replace(reg2,"")+"00")
    console.log(this.e_time1.toString().replace(reg1,"")+this.e_time2.toString().replace(reg2,"")+"00")
    console.log(this.user_id)
    console.log(this.att_nums)

    axios.post( `${ServiceUrl}/previewRoom`,
    {
      user_id:this.user_id,
      att_nums:this.att_nums,
      s_time:this.s_time1.toString().replace(reg1,"")+this.s_time2.toString().replace(reg2,"")+"00",
      e_time:this.e_time1.toString().replace(reg1,"")+this.e_time2.toString().replace(reg2,"")+"00"
    },
    {
      headers: {
        'Content-Type': 'application/json',
        "Access-Control-Allow-Origin": "*",
        'Accept': 'application/json'
      },
    }
    ).then(resp => {
        this.setState({
          showData:resp.data.data
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
                <i className="fa fa-align-justify"></i> 显示信息
              </CardHeader>
              <CardBody>
                <Table responsive>
                  <thead>
                  <tr fix>
                    <th>编号</th>
                    <th>会议室门牌</th>
                    <th>容纳人数</th>
                  </tr>
                  </thead>
                  <tbody>
                  {
                    this.state.showData.map(function (each, idx) {
                      return(
                        <tr key={idx}>
                          <td >{each[0]}</td>
                          <td >{each[1]}</td>
                          <td >{each[2]}</td>
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
                <strong>预约信息输入</strong>
              </CardHeader>
              <CardBody>
                <FormGroup>
                  <Label htmlFor="QQ">预约人员</Label>
                  <Input type="text" id="userInfo" onChange={event => (this.user_id =event.target.value)} placeholder="刘XX" />
                  开始日期：<Input type="date" id="s_time" onChange={event => (this.s_time1 =event.target.value)}/>
                  具体时间：<Input type="time" id="s_time" onChange={event => (this.s_time2 =event.target.value)}/>
                  结束日期：<Input type="date" id="e_time" onChange={event => (this.e_time1 =event.target.value)}/>
                  具体时间：<Input type="time" id="e_time" onChange={event => (this.e_time2 =event.target.value)}/>
                  参会人数：<Input type="text" id="e_time" onChange={event => (this.att_nums =event.target.value)}/>
                </FormGroup>
              </CardBody>
              <CardFooter>
                <span style={{ marginLeft: '12rem' }}></span>
                <Button type="submit" size="sm" onClick={this.searchDate} color="primary"><i className="fa fa-dot-circle-o"></i> 预约会议室</Button>
              </CardFooter>
            </Card>
          </Col>
        </Row>
      </div>
    );
  }
}

export default Search;
