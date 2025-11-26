import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, Button, Typography, Space, message, Spin, Modal } from 'antd';
import { ArrowLeftOutlined, CheckOutlined, GithubOutlined } from '@ant-design/icons';
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer-continued';
import { generateFix, createPR } from '../api/endpoints';
import { Issue, RepoInfo } from '../types';

const { Title, Paragraph, Text } = Typography;

const FixPreview: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { issue, fileContent, repoInfo } = location.state as { issue: Issue, fileContent: string, repoInfo: RepoInfo };

  const [fixedContent, setFixedContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!issue || !fileContent) {
        navigate('/dashboard');
        return;
    }

    const fetchFix = async () => {
      try {
        const res = await generateFix(issue.file, issue.id, fileContent);
        setFixedContent(res.fixed_content);
      } catch (error) {
        console.error(error);
        message.error('生成修复内容失败');
      } finally {
        setLoading(false);
      }
    };

    fetchFix();
  }, [issue, fileContent, navigate]);

  const handleCreatePR = async () => {
      setSubmitting(true);
      try {
          // In a real scenario, we would generate a unique branch name
          const branchName = `docs/fix-${issue.id}-${Date.now()}`;
          const changes = { [issue.file]: fixedContent };
          
          const res = await createPR(repoInfo.repo, branchName, changes);
          
          Modal.success({
              title: 'PR 创建成功',
              content: (
                  <div>
                      <p>已成功为您创建 Pull Request！</p>
                      <a href={res.pr_url} target="_blank" rel="noopener noreferrer">点击查看 PR</a>
                  </div>
              ),
              onOk: () => navigate('/dashboard'),
          });
      } catch (error) {
          console.error(error);
          message.error('创建 PR 失败，请确保您已登录并授权');
      } finally {
          setSubmitting(false);
      }
  };

  if (loading) {
      return (
          <div style={{ textAlign: 'center', padding: '100px' }}>
              <Spin size="large" tip="正在生成修复方案..." />
          </div>
      );
  }

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        返回报告
      </Button>

      <Card title={`修复预览: ${issue.file}`} extra={
          <Button type="primary" icon={<GithubOutlined />} loading={submitting} onClick={handleCreatePR}>
              提交 PR
          </Button>
      }>
        <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
            <Paragraph>
                针对问题 <Text code>{issue.description}</Text> 的自动修复建议。
            </Paragraph>
        </Space>
        
        <div style={{ maxHeight: '600px', overflow: 'auto', border: '1px solid #e8e8e8', borderRadius: '4px' }}>
            <ReactDiffViewer 
                oldValue={fileContent} 
                newValue={fixedContent} 
                splitView={true}
                compareMethod={DiffMethod.WORDS}
                leftTitle="当前内容"
                rightTitle="修复后内容"
            />
        </div>
      </Card>
    </div>
  );
};

export default FixPreview;
