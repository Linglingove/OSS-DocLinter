import React from 'react';
import { Layout as AntLayout, Menu, Button, Avatar, Dropdown, message } from 'antd';
import { UserOutlined, GithubOutlined, LogoutOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getLoginUrl } from '../api/endpoints';

const { Header, Content, Footer } = AntLayout;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');
  
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/');
    window.location.reload();
  };

  const userMenu = (
    <Menu>
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        退出登录
      </Menu.Item>
    </Menu>
  );

  return (
    <AntLayout className="layout" style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div className="logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
          OSS-DocLinter
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
            {token ? (
                 <Dropdown overlay={userMenu} placement="bottomRight">
                    <Avatar icon={<UserOutlined />} style={{ cursor: 'pointer' }} />
                 </Dropdown>
            ) : (
                <Button type="primary" icon={<GithubOutlined />} onClick={async () => {
                    try {
                        const { login_url } = await getLoginUrl();
                        window.location.href = login_url;
                    } catch (error) {
                        console.error(error);
                        message.error('获取登录链接失败，请检查后端服务');
                    }
                }}>
                    GitHub 登录
                </Button>
            )}
        </div>
      </Header>
      <Content style={{ padding: '0 50px' }}>
        <div className="site-layout-content" style={{ marginTop: '24px', background: '#fff', padding: '24px', minHeight: '380px' }}>
          {children}
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        OSS-DocLinter ©{new Date().getFullYear()} Created by Open Source Community
      </Footer>
    </AntLayout>
  );
};

export default Layout;
