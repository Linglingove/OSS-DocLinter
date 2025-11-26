import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { message, Spin } from 'antd';
import { exchangeToken } from '../api/endpoints';

const Callback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const code = searchParams.get('code');

  useEffect(() => {
    const handleCallback = async () => {
      if (!code) {
        message.error('未获取到授权码');
        navigate('/');
        return;
      }

      try {
        const data = await exchangeToken(code);
        localStorage.setItem('access_token', data.access_token);
        message.success('登录成功');
        navigate('/');
      } catch (error) {
        console.error(error);
        message.error('登录失败，请重试');
        navigate('/');
      }
    };

    handleCallback();
  }, [code, navigate]);

  return (
    <div style={{ textAlign: 'center', padding: '100px' }}>
      <Spin size="large" tip="正在处理登录..." />
    </div>
  );
};

export default Callback;
