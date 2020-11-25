import React, { Component } from 'react';
import { Link,Redirect } from 'react-router-dom';
import { Button, Card, CardBody, CardGroup, Col, Container, Form, Input, InputGroup, InputGroupAddon, InputGroupText, Row } from 'reactstrap';
import {login} from '../../../redux/actions/loginAction'
import {connect} from "react-redux"
class Login extends Component {
  constructor(props) {;
    super(props)
    this.state = {
      username: "",
      password: "",
      auth_:false,
    }
  }

  handleChange = (e) =>{
    const name = e.target.name
    const value = e.target.value
    this.setState({
      [name]: value,
    });
  }

  handleClick = () =>{
    const userInfo = {
      username:this.state.username,
      password:this.state.password,
    }
    this.setState({
      auth_:!this.state.auth
    },console.log(this.state));
    // this.props.dispatch(login(userInfo))
    // console.log(this.props)


  }

  render() {
    // const{ isAuthenticated } = 
    // console.log("isAuthenticated",isAuthenticated)
    console.log(this.state.auth_)
    return (
      <div className="app flex-row align-items-center">
        <Container>
          <Row className="justify-content-center">
            <Col md="8">
              <CardGroup>
                <Card className="p-4">
                  <CardBody>
                    <Form>
                      <h1>Login</h1>
                      <p className="text-muted">Sign In to your account</p>
                      <InputGroup className="mb-3">
                        <InputGroupAddon addonType="prepend">
                          <InputGroupText>
                            <i className="icon-user"></i>
                          </InputGroupText>
                        </InputGroupAddon>
                        <Input type="text" placeholder="Username" name="username" onChange={this.handleChange} autoComplete="username" />
                      </InputGroup>
                      <InputGroup className="mb-4">
                        <InputGroupAddon addonType="prepend">
                          <InputGroupText>
                            <i className="icon-lock"></i>
                          </InputGroupText>
                        </InputGroupAddon>
                        <Input type="password" placeholder="Password" name="password" onChange={this.handleChange} autoComplete="current-password" />
                      </InputGroup>
                      <Row>
                        <Col xs="6">
                          <Button color="primary" onClick={(event)=> this.handleClick(event)} className="px-4">Login</Button>
                        </Col>
                        <Col xs="6" className="text-right">
                          <Button color="link" className="px-0">Forgot password?</Button>
                        </Col>
                      </Row>
                    </Form>
                  </CardBody>
                </Card>
                <Card className="text-white bg-primary py-5 d-md-down-none" style={{ width: '44%' }}>
                  <CardBody className="text-center">
                    <div>
                      <h2>Sign up</h2>
                      <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut
                        labore et dolore magna aliqua.</p>
                      <Link to="/register">
                        <Button color="primary" className="mt-3" active tabIndex={-1}>Register Now!</Button>
                      </Link>
                    </div>
                  </CardBody>
                </Card>
              </CardGroup>
              {this.state.auth_ && <Redirect to="/dashboard"/>}
            </Col>
          </Row>
        </Container>
      </div>
    );
  }
}
// Login.prototype ={
//   dispatch: prototype.func.isr
// }

function mapStateToProps(state){
  return{
    auth:state.auth
  }
}
export default connect(mapStateToProps)(Login);
