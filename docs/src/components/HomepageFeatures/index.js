import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: '无门槛入门',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        只要编写Python的函数，就可以轻松构建一个命令行应用。
      </>
    ),
  },
  {
    title: '丰富模板库',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        QuickProject提供了丰富的<b>基础模板</b>和<b>高级模板</b>，帮助快速创建某程序语言的<b><i>样例程序</i></b>，亦或者稍复杂但开箱即用的<b><i>模板工程</i></b>。
      </>
    ),
  },
  {
    title: '全套工具箱',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        QuickProject与QuickStart_Rhy搭配，专注实现业务流程，无需考虑下载、解压、依赖库引导安装等各种常见问题。
      </>
    ),
  },
];

function Feature({ Svg, title, description }) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
