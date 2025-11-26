import React, { useState } from 'react';
import { Input, Button, Typography, Card, Space, message, Row, Col, Statistic } from 'antd';
import { SearchOutlined, RocketOutlined, SafetyCertificateOutlined, BulbOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { analyzeRepo } from '../api/endpoints';

const { Title, Paragraph, Text } = Typography;

const Home: React.FC = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (!url) {
      message.error('请输入 GitHub 仓库地址');
      return;
    }
    
    if (!url.includes('github.com')) {
        message.warning('目前仅支持 GitHub 仓库');
    }

    setLoading(true);
    try {
      const data = await analyzeRepo(url);
      navigate('/dashboard', { state: { data } });
    } catch (error) {
      console.error(error);
      message.error('分析失败，请检查 URL 或稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px 0' }}>

      <div style={{ textAlign: 'center', marginBottom: '80px' }} className="fade-in">
        <Space direction="vertical" size="large" style={{ width: '100%', maxWidth: '900px' }}>
          <div style={{ 
            background: '#e6f7ff', 
            display: 'inline-block', 
            padding: '20px', 
            borderRadius: '50%', 
            marginBottom: '20px',
            border: '1px solid #bae7ff'
          }}>
            <RocketOutlined style={{ fontSize: '64px', color: '#1890ff' }} />
          </div>
          
          <Title level={1} style={{ fontSize: '48px', marginBottom: '16px', fontWeight: 800 }}>
            OSS-DocLinter
          </Title>
          
          <Paragraph style={{ fontSize: '20px', color: '#666', maxWidth: '700px', margin: '0 auto 40px' }}>
            开源项目文档质量自动化分析工具。
            <br />
            一键扫描核心文档，获取<Text strong type="success">完整性</Text>与<Text strong type="warning">规范性</Text>评分及智能改进建议。
          </Paragraph>

          <Card 
            bordered={false} 
            className="glass-card"
            style={{ 
              boxShadow: '0 8px 24px rgba(0,0,0,0.08)', 
              borderRadius: '16px',
              padding: '10px'
            }}
          >
            <Space.Compact style={{ width: '100%' }} size="large">
              <Input 
                placeholder="请输入 GitHub 仓库地址 (例如: https://github.com/facebook/react)" 
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onPressEnter={handleAnalyze}
                prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />}
                style={{ fontSize: '16px', padding: '12px 20px' }}
              />
              <Button 
                type="primary" 
                loading={loading} 
                onClick={handleAnalyze}
                style={{ height: 'auto', padding: '0 30px', fontSize: '16px', fontWeight: 600 }}
              >
                开始分析
              </Button>
            </Space.Compact>
          </Card>
        </Space>
      </div>

      <div className="fade-in-delay-1">
        <Title level={2} style={{ textAlign: 'center', marginBottom: '40px' }}>为什么选择 OSS-DocLinter?</Title>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <Card className="feature-card" bordered={false}>
              <div style={{ textAlign: 'center' }}>
                <SafetyCertificateOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '20px' }} />
                <Title level={4}>自动化评估</Title>
                <Paragraph type="secondary">
                  告别繁琐的人工审查。系统自动扫描 README、CONTRIBUTING 等文件，快速定位文档缺失和格式错误。
                </Paragraph>
              </div>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card className="feature-card" bordered={false}>
              <div style={{ textAlign: 'center' }}>
                <BulbOutlined style={{ fontSize: '48px', color: '#faad14', marginBottom: '20px' }} />
                <Title level={4}>智能建议</Title>
                <Paragraph type="secondary">
                  基于 LLM 的深度语义分析，为您提供具体的文档改进建议，不仅仅是格式检查，更是内容优化。
                </Paragraph>
              </div>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card className="feature-card" bordered={false}>
              <div style={{ textAlign: 'center' }}>
                <ThunderboltOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '20px' }} />
                <Title level={4}>一键修复</Title>
                <Paragraph type="secondary">
                  发现问题后，一键生成修复后的文档内容，并自动提交 Pull Request，让文档维护变得前所未有的简单。
                </Paragraph>
              </div>
            </Card>
          </Col>
        </Row>
      </div>

      <div style={{ marginTop: '80px', textAlign: 'center' }} className="fade-in-delay-2">
        <Row gutter={16} justify="center">
          <Col span={6}>
            <Statistic title="已分析项目" value={1208} prefix={<RocketOutlined />} />
          </Col>
          <Col span={6}>
            <Statistic title="发现问题" value={5432} prefix={<SafetyCertificateOutlined />} />
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Home;
