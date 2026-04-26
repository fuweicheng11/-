<template>
  <div class="app-shell" :class="{ 'mobile-app': isMobile }">
    <el-container>
      <el-aside v-if="!isMobile" width="248px" class="sidebar">
        <div class="panel brand-panel">
          <p class="eyebrow">Camouflage Insect Lab</p>
          <h2>伪装昆虫识别平台</h2>
          <p class="muted">面向复杂自然背景的图像识别、结果复核与昆虫知识分析平台。</p>
        </div>
        <div class="panel nav-panel">
          <button
            v-for="item in navItems"
            :key="item.screen"
            type="button"
            class="nav-btn"
            :class="{ active: currentGroup === item.screen }"
            @click="openScreen(item.screen)"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </button>
        </div>
      </el-aside>

      <el-main class="main">
        <header v-if="!isMobile" class="topbar">
          <div>
            <p class="eyebrow">{{ meta.kicker }}</p>
            <h1>{{ meta.title }}</h1>
            <p v-if="meta.desc" class="muted">{{ meta.desc }}</p>
          </div>
          <div class="topbar-actions">
            <el-tag v-if="currentUser" round type="success">{{ currentUser.role === 'admin' ? '管理员' : '用户' }}</el-tag>
            <el-button circle @click="loadBootstrap(screen, recordId)">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </header>

        <el-alert v-if="boot.error" :title="boot.error" type="error" show-icon class="block-gap" />

        <div v-loading="pageLoading" element-loading-text="正在加载页面">
          <section v-show="screen === 'home'" class="block-gap">
            <div v-if="isMobile" class="mobile-home">
              <div class="mobile-home-top">
                <div class="location-pill">
                  <el-icon><LocationFilled /></el-icon>
                  <span>{{ mobileLocationText }}</span>
                </div>
                <div class="mobile-home-actions">
                  <button type="button" class="icon-chip" @click="cycleHomeTab">
                    <el-icon><MoreFilled /></el-icon>
                  </button>
                  <button type="button" class="icon-chip" @click="pick('gallery')">
                    <el-icon><Plus /></el-icon>
                  </button>
                </div>
              </div>

              <div class="mobile-home-tabs">
                <button
                  v-for="item in homeTabs"
                  :key="item.key"
                  type="button"
                  class="home-tab"
                  :class="{ active: homeTab === item.key }"
                  @click="homeTab = item.key"
                >
                  {{ item.label }}
                </button>
              </div>

              <article class="hero-card cover-showcase-card">
                <div class="cover-showcase-copy">
                  <p class="hero-kicker">{{ showcaseHeadline.kicker }}</p>
                  <h3>{{ showcaseHeadline.title }}</h3>
                  <p>{{ showcaseHeadline.summary }}</p>
                </div>
                <div class="showcase-window">
                  <div class="showcase-track">
                    <button
                      v-for="(item, index) in showcaseRail"
                      :key="`${item.key}-${index}`"
                      type="button"
                      class="showcase-slide"
                      @click="runSample(item.key)"
                    >
                      <img :src="item.image_url" :alt="item.title">
                      <div class="showcase-caption">
                        <strong>{{ item.title }}</strong>
                        <span>{{ item.subtitle }}</span>
                      </div>
                    </button>
                  </div>
                </div>
              </article>

              <section class="feed-list">
                <div v-if="homeTab === 'feed'" class="feed-section-head">
                  <div>
                    <p class="eyebrow">最近更新</p>
                    <h3>观察动态</h3>
                  </div>
                  <el-button type="primary" plain size="small" @click="openPostComposer">我也发一张</el-button>
                </div>
                <article
                  v-for="item in currentHomeItems"
                  :key="item.id || item.key || item.title"
                  class="feed-card"
                  @click="handleHomeCard(item)"
                >
                  <div class="feed-copy">
                    <span class="feed-tag">{{ item.tag }}</span>
                    <h4>{{ item.title }}</h4>
                    <p>{{ item.summary }}</p>
                    <div class="feed-meta">
                      <span class="feed-author">
                        <img :src="item.author_avatar || beeAvatar" :alt="item.author">
                        <span>{{ item.author }}</span>
                      </span>
                      <span>{{ item.meta }}</span>
                    </div>
                    <a v-if="item.url" class="feed-link" :href="item.url" target="_blank" rel="noopener noreferrer" @click.stop>查看来源</a>
                  </div>
                  <img :src="item.image_url" :alt="item.title">
                </article>
              </section>
            </div>

            <template v-else>
              <el-row :gutter="16">
                <el-col :xs="24" :lg="15">
                  <el-card shadow="never" class="panel-card block-gap insect-panel">
                    <div class="desktop-home-banner">
                      <div class="desktop-banner-copy">
                        <p class="eyebrow">{{ showcaseHeadline.kicker }}</p>
                        <h3>{{ showcaseHeadline.title }}</h3>
                        <p class="muted">{{ showcaseHeadline.summary }}</p>
                        <el-button type="primary" @click="openScreen('identify')">开始识别</el-button>
                      </div>
                      <div class="desktop-banner-side">
                        <div class="showcase-window showcase-window-desktop">
                          <div class="showcase-track">
                            <button
                              v-for="(item, index) in showcaseRail"
                              :key="`desktop-${item.key}-${index}`"
                              type="button"
                              class="showcase-slide"
                              @click="runSample(item.key)"
                            >
                              <img :src="item.image_url" :alt="item.title">
                              <div class="showcase-caption">
                                <strong>{{ item.title }}</strong>
                                <span>{{ item.subtitle }}</span>
                              </div>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </el-card>

                  <el-card shadow="never" class="panel-card">
                    <template #header>
                      <div class="head-row">
                        <div><p class="eyebrow">最近更新</p><h3>观察动态</h3></div>
                        <el-button type="primary" plain size="small" @click="openPostComposer">我也发一张</el-button>
                      </div>
                    </template>
                    <div class="desktop-feed-grid">
                      <article v-for="item in desktopHomePosts" :key="item.id || item.title" class="desktop-feed-card">
                        <img :src="item.image_url" :alt="item.title">
                        <div>
                          <span class="feed-tag">{{ item.tag }}</span>
                          <h4>{{ item.title }}</h4>
                          <p>{{ item.summary }}</p>
                          <div class="feed-meta">
                            <span class="feed-author">
                              <img :src="item.author_avatar || beeAvatar" :alt="item.author">
                              <span>{{ item.author }}</span>
                            </span>
                            <span>{{ item.meta }}</span>
                          </div>
                        </div>
                      </article>
                    </div>
                  </el-card>
                </el-col>

                <el-col :xs="24" :lg="9">
                  <el-card shadow="never" class="panel-card block-gap">
                    <template #header>
                      <div class="head-row"><div><p class="eyebrow">文章精选</p><h3>识别阅读</h3></div></div>
                    </template>
                    <div class="desktop-side-list">
                      <article
                        v-for="item in desktopArticles"
                        :key="item.title"
                        class="side-list-item side-list-link"
                        @click="handleHomeCard(item)"
                      >
                        <span class="feed-tag">{{ item.tag }}</span>
                        <strong>{{ item.title }}</strong>
                        <p>{{ item.summary }}</p>
                        <span class="paper-source">{{ item.author }} · {{ item.meta }}</span>
                        <a
                          v-if="item.url"
                          class="paper-link"
                          :href="item.url"
                          target="_blank"
                          rel="noopener noreferrer"
                          @click.stop
                        >
                          查看原文
                        </a>
                      </article>
                    </div>
                  </el-card>

                </el-col>
              </el-row>
            </template>
          </section>

          <section v-show="screen === 'taxonomy'" class="block-gap">
            <el-card shadow="never" class="panel-card taxonomy-panel">
              <div class="taxonomy-toolbar">
                <el-select v-model="taxonomyGroup" class="taxonomy-select">
                  <el-option v-for="item in taxonomyGroupOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
                <el-input v-model.trim="taxonomyQuery" clearable placeholder="搜索中文名、英文名或拉丁学名" class="taxonomy-search">
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-tag round effect="plain" type="success">已收录 {{ taxonomyOrders.length }} 个目级类群</el-tag>
              </div>

              <div class="taxonomy-layout">
                <div class="taxonomy-main">
                  <section
                    v-for="order in taxonomyOrders"
                    :id="`taxonomy-${order.id}`"
                    :key="order.id"
                    class="taxonomy-section"
                  >
                    <div class="taxonomy-order-bar">
                      <span class="taxonomy-level-chip taxonomy-level-chip-order">目</span>
                      <span class="taxonomy-order-cn">{{ order.order_cn }}</span>
                      <span class="taxonomy-order-latin">{{ order.order_latin }}</span>
                      <span class="taxonomy-order-meta">{{ order.subgroup_count }} 个类群 · {{ order.species_count }} 个代表物种</span>
                    </div>

                    <details class="taxonomy-overview" :open="false">
                      <summary class="taxonomy-overview-summary">
                        <img class="taxonomy-overview-avatar" :src="order.focus_image" :alt="order.focus_cn">
                        <span class="taxonomy-level-chip taxonomy-level-chip-family">目级总览</span>
                        <strong>{{ order.focus_cn }}</strong>
                        <em>{{ order.focus_latin }}</em>
                        <span class="taxonomy-overview-toggle">点展开</span>
                      </summary>

                      <div class="taxonomy-overview-body">
                        <article class="taxonomy-focus-card taxonomy-overview-card">
                          <img :src="order.focus_image" :alt="order.focus_cn">
                          <div class="taxonomy-focus-copy">
                            <h3>{{ order.focus_cn }}</h3>
                            <p>{{ order.focus_en }}</p>
                            <i>{{ order.focus_latin }}</i>
                            <p class="muted">{{ order.summary }}</p>
                          </div>
                        </article>

                        <div v-if="order.families.length" class="taxonomy-family-list">
                          <details
                            v-for="(family, familyIndex) in order.families"
                            :key="family.id"
                            class="taxonomy-family"
                            :open="familyIndex === 0"
                          >
                            <summary class="taxonomy-family-summary">
                              <img :src="family.cover_image" :alt="family.family_cn">
                              <div class="taxonomy-family-copy">
                                <span class="taxonomy-level-chip taxonomy-level-chip-family">科 / 类群</span>
                                <strong>{{ family.family_cn }}</strong>
                                <span>{{ family.family_en }}</span>
                                <em>{{ family.family_latin }}</em>
                                <p class="muted">{{ family.summary }}</p>
                              </div>
                              <span class="taxonomy-family-toggle">展开类群</span>
                            </summary>

                            <div class="taxonomy-family-body">
                              <div v-if="family.species.length" class="taxonomy-species-list">
                                <button
                                  v-for="item in family.species"
                                  :key="item.id"
                                  type="button"
                                  class="taxonomy-species-card"
                                  @click="openTaxonomyLink(item.url)"
                                >
                                  <div class="taxonomy-species-thumb" :class="{ 'is-generic': item.image_is_generic }">
                                    <img v-if="item.image" :src="item.image" :alt="item.name_cn">
                                    <div v-else class="taxonomy-species-placeholder">
                                      <el-icon><Picture /></el-icon>
                                      <span>待补物种图</span>
                                    </div>
                                  </div>
                                  <div class="taxonomy-species-copy">
                                    <span class="taxonomy-level-chip taxonomy-level-chip-species">物种</span>
                                    <strong>{{ item.name_cn }}</strong>
                                    <span>{{ item.name_en }}</span>
                                    <em>{{ item.latin }}</em>
                                  </div>
                                </button>
                              </div>
                            </div>
                          </details>
                        </div>
                      </div>
                    </details>
                  </section>

                  <el-empty v-if="!taxonomyOrders.length" description="没有匹配到相关类群，试试换个关键词。" />
                </div>

                <aside class="taxonomy-rail">
                  <button
                    v-for="order in taxonomyOrders"
                    :key="`rail-${order.id}`"
                    type="button"
                    class="taxonomy-rail-item"
                    @mousedown.prevent
                    @click="jumpToTaxonomy(order.id, $event)"
                  >
                    <span class="taxonomy-rail-cn">{{ order.order_cn }}</span>
                  </button>
                </aside>
              </div>
            </el-card>
          </section>

          <section v-show="screen === 'identify'" class="block-gap">
            <el-card shadow="never" class="panel-card insect-panel">
              <template #header>
                <div class="head-row">
                  <div>
                    <p class="eyebrow">图像识别</p>
                    <h3>上传昆虫图像并开始分析</h3>
                  </div>
                  <el-tag type="success" effect="plain">识别完成后自动进入结果页</el-tag>
                </div>
              </template>
              <p class="muted">支持相册导入、移动端拍照和标准样例识别。</p>
              <div class="action-row block-gap-sm">
                <label
                  for="gallery-picker"
                  class="action-label action-label-primary"
                  :class="{ disabled: analyzeLoading }"
                >
                  <span class="action-label-inner">
                    <el-icon><UploadFilled /></el-icon>
                    选择图片
                  </span>
                </label>
                <label
                  for="camera-picker"
                  class="action-label"
                  :class="{ disabled: analyzeLoading }"
                >
                  <span class="action-label-inner">
                    <el-icon><CameraFilled /></el-icon>
                    打开相机
                  </span>
                </label>
              </div>
              <div class="preview-box" :class="{ empty: !preview }">
                <template v-if="preview">
                  <img :src="preview" alt="待识别图片">
                  <div class="preview-copy">
                    <strong>{{ previewName }}</strong>
                    <span>图像已加载完成，正在调用识别链路。</span>
                  </div>
                </template>
                <template v-else>
                  <el-icon><Picture /></el-icon>
                  <p>上传图片后，这里会显示当前待识别图像。</p>
                </template>
              </div>
            </el-card>

            <el-card shadow="never" class="panel-card block-gap">
              <template #header>
                <div class="head-row">
                  <div>
                    <p class="eyebrow">标准样例</p>
                    <h3>快速测试</h3>
                  </div>
                </div>
              </template>
              <div class="sample-grid">
                <button v-for="item in samples.slice(0, 6)" :key="item.key" type="button" class="sample-item" @click="runSample(item.key)">
                  <img :src="item.image_url" :alt="item.title">
                  <div>
                    <strong>{{ item.title }}</strong>
                    <span>{{ item.subtitle }}</span>
                  </div>
                </button>
              </div>
            </el-card>
          </section>

          <section v-show="screen === 'result'" class="block-gap">
            <template v-if="result">
              <el-row :gutter="16">
                <el-col :xs="24" :lg="14">
                  <el-card shadow="never" class="panel-card block-gap">
                    <template #header>
                      <div class="head-row"><div><p class="eyebrow">识别图像</p><h3>原图</h3></div></div>
                    </template>
                    <el-image :src="processImages[0]?.src" :preview-src-list="processPreview" fit="cover" class="main-image" />
                  </el-card>

                  <el-card v-if="evidenceImages.length" shadow="never" class="panel-card">
                    <template #header>
                      <div class="head-row"><div><p class="eyebrow">分类证据</p><h3>解释结果</h3></div></div>
                    </template>
                    <div class="evidence-grid evidence-grid-wide">
                      <article v-for="(item, index) in evidenceImages" :key="item.label" class="mini-card evidence-card">
                        <el-image :src="item.src" :preview-src-list="evidencePreview" :initial-index="index" fit="cover" class="mini-image" />
                        <span>{{ item.label }}</span>
                      </article>
                    </div>
                  </el-card>
                </el-col>

                <el-col :xs="24" :lg="10">
                  <el-card shadow="never" class="panel-card block-gap">
                    <template #header>
                      <div class="head-row">
                        <div><p class="eyebrow">分类结果</p><h3>{{ result.classification.label }}</h3></div>
                        <el-button v-if="currentUser && result.record_id" type="danger" plain size="small" @click="removeHistory(result.record_id)">删除记录</el-button>
                      </div>
                    </template>
                    <p class="muted">{{ result.classification.decision_text }}</p>
                    <div class="metric-grid">
                      <article v-for="item in metrics" :key="item.label" class="mini-card">
                        <span>{{ item.label }}</span>
                        <strong>{{ item.value }}</strong>
                      </article>
                    </div>
                  </el-card>

                  <el-card shadow="never" class="panel-card block-gap">
                    <template #header>
                      <div class="head-row"><div><p class="eyebrow">科普信息</p><h3>{{ result.science.title }}</h3></div></div>
                    </template>
                    <div class="science-list">
                      <p><b>伪装方式：</b>{{ result.science.camouflage }}</p>
                      <p><b>识别线索：</b>{{ result.science.clue }}</p>
                      <p><b>生态角色：</b>{{ result.science.role }}</p>
                      <p><b>风险影响：</b>{{ result.science.impact }}</p>
                      <p><b>处理建议：</b>{{ result.science.advice }}</p>
                    </div>
                  </el-card>

                  <el-card shadow="never" class="panel-card">
                    <template #header>
                      <div class="head-row">
                        <div><p class="eyebrow">DeepSeek 问答</p><h3>结果追问</h3></div>
                        <el-tag :type="assistantEnabled ? 'success' : 'info'" effect="plain">{{ assistantEnabled ? '远程问答已启用' : '当前使用本地知识回答' }}</el-tag>
                      </div>
                    </template>
                    <div class="quick-question-row">
                      <button v-for="item in quickQuestions" :key="item" type="button" class="quick-chip" @click="assistantQuestion = item">{{ item }}</button>
                    </div>
                    <el-input v-model="assistantQuestion" type="textarea" :rows="4" resize="none" placeholder="例如：这种昆虫是否具有危害性？主要出现在哪些环境中？" />
                    <div class="action-row block-gap-sm">
                      <el-button type="primary" :loading="assistantLoading" @click="askAssistant">发送问题</el-button>
                      <el-button v-if="assistantQuestion" @click="assistantQuestion = ''">清空</el-button>
                    </div>
                    <div class="answer-box" :class="{ empty: !assistantAnswer }">{{ assistantAnswer || '识别完成后，可继续围绕生态角色、风险影响和处理建议进行追问。' }}</div>
                  </el-card>
                </el-col>
              </el-row>
            </template>
            <el-empty v-else description="当前没有可展示的识别结果">
              <el-button type="primary" @click="openScreen('identify')">前往识别</el-button>
            </el-empty>
          </section>

          <section v-show="screen === 'mine'" class="block-gap">
            <template v-if="currentUser">
              <el-card shadow="never" class="panel-card block-gap insect-panel">
                <div class="profile">
                  <div class="avatar avatar-photo">
                    <img :src="currentUserAvatar" :alt="currentUser.display_name">
                  </div>
                  <div class="profile-copy">
                    <strong>{{ currentUser.display_name }}</strong>
                    <p>@{{ currentUser.username }}</p>
                    <span>{{ currentUser.role === 'admin' ? '管理员账号' : '用户账号' }}</span>
                    <div class="avatar-tools">
                      <el-button size="small" plain @click="avatarInput?.click()">上传头像</el-button>
                    </div>
                  </div>
                  <div class="topbar-actions">
                    <el-button @click="logout">退出登录</el-button>
                    <el-button v-if="currentUser.role === 'user'" type="danger" plain @click="removeAccount">删除账号</el-button>
                    <el-button v-if="currentUser.role === 'admin'" type="primary" plain @click="openScreen('admin')">进入后台</el-button>
                  </div>
                </div>
              </el-card>

              <el-card shadow="never" class="panel-card">
                <template #header>
                  <div class="head-row"><div><p class="eyebrow">识别历史</p><h3>当前账号记录</h3></div></div>
                </template>
                <div v-if="history.length" class="history-grid">
                  <article v-for="item in history" :key="item.record_id" class="history-item">
                    <button type="button" class="sample-item history-main" @click="openResult(item.record_id)">
                      <img v-if="item.thumbnail_src" :src="item.thumbnail_src" :alt="item.label">
                      <div>
                        <strong>{{ item.label }}</strong>
                        <p>{{ item.decision_text }}</p>
                        <span>{{ item.created_at }}</span>
                      </div>
                    </button>
                    <el-button type="danger" plain size="small" @click="removeHistory(item.record_id)">删除</el-button>
                  </article>
                </div>
                <el-empty v-else description="当前账号下还没有识别记录" />
              </el-card>

              <el-card v-if="currentUser.role === 'user'" shadow="never" class="panel-card">
                <template #header>
                  <div class="head-row">
                    <div><p class="eyebrow">我的动态</p><h3>已发布内容</h3></div>
                    <el-button type="primary" plain size="small" @click="openPostComposer">我也发一张</el-button>
                  </div>
                </template>
                <div v-if="userPosts.length" class="post-history-grid">
                  <article v-for="item in userPosts" :key="item.id" class="post-history-card">
                    <img v-if="item.image_src" :src="item.image_src" :alt="item.title" class="post-history-media">
                    <div class="post-history-copy">
                      <span class="feed-tag">{{ item.tag }}</span>
                      <strong>{{ item.title }}</strong>
                      <p>{{ item.summary }}</p>
                      <div class="feed-meta">
                        <span>{{ item.meta }}</span>
                      </div>
                    </div>
                    <el-button type="danger" plain size="small" @click="removePost(item.id)">删除</el-button>
                  </article>
                </div>
                <el-empty v-else description="还没有发布过动态，去首页发第一条吧" />
              </el-card>
            </template>

            <el-card v-else shadow="never" class="panel-card auth-card">
              <div class="auth-title">
                <p class="eyebrow">账号中心</p>
                <h3>登录或注册</h3>
                <p class="muted">登录后即可保存个人识别记录，并在“我的”页面随时回看。</p>
              </div>
              <el-tabs v-model="authTab" stretch>
                <el-tab-pane label="用户登录" name="login">
                  <el-form @submit.prevent="loginUser">
                    <el-form-item label="用户名"><el-input v-model.trim="loginForm.username" autocomplete="username" /></el-form-item>
                    <el-form-item label="密码"><el-input v-model="loginForm.password" type="password" show-password autocomplete="current-password" /></el-form-item>
                    <el-button type="primary" :loading="authLoading" @click="loginUser">登录</el-button>
                  </el-form>
                </el-tab-pane>
                <el-tab-pane label="用户注册" name="register">
                  <el-form @submit.prevent="registerUser">
                    <el-form-item label="昵称"><el-input v-model.trim="registerForm.display_name" autocomplete="off" /></el-form-item>
                    <el-form-item label="用户名"><el-input v-model.trim="registerForm.username" autocomplete="off" /></el-form-item>
                    <el-form-item label="密码"><el-input v-model="registerForm.password" type="password" show-password autocomplete="new-password" /></el-form-item>
                    <el-button type="primary" :loading="authLoading" @click="registerUser">创建账号</el-button>
                  </el-form>
                </el-tab-pane>
                <el-tab-pane v-if="!isMobile" label="管理员登录" name="admin">
                  <el-form @submit.prevent="loginAdmin">
                    <el-form-item label="管理员用户名"><el-input v-model.trim="adminLoginForm.username" autocomplete="username" /></el-form-item>
                    <el-form-item label="密码"><el-input v-model="adminLoginForm.password" type="password" show-password autocomplete="current-password" /></el-form-item>
                    <el-button type="primary" :loading="authLoading" @click="loginAdmin">登录后台</el-button>
                  </el-form>
                </el-tab-pane>
              </el-tabs>
            </el-card>
          </section>

          <section v-if="isAdmin" v-show="screen === 'admin'" class="block-gap">
            <el-row :gutter="16">
              <el-col :xs="24" :lg="10">
                <el-card shadow="never" class="panel-card block-gap">
                  <template #header>
                    <div class="head-row"><div><p class="eyebrow">后台概览</p><h3>运行状态</h3></div></div>
                  </template>
                  <div class="metric-grid">
                    <article class="mini-card"><span>用户数</span><strong>{{ adminOverview?.user_count ?? 0 }}</strong></article>
                    <article class="mini-card"><span>识别记录</span><strong>{{ adminOverview?.history_count ?? 0 }}</strong></article>
                    <article class="mini-card"><span>数据库</span><strong>{{ adminOverview?.db_name || '-' }}</strong></article>
                    <article class="mini-card"><span>主机</span><strong>{{ adminOverview?.db_host || '-' }}</strong></article>
                  </div>
                </el-card>

                <el-card shadow="never" class="panel-card">
                  <template #header>
                    <div class="head-row"><div><p class="eyebrow">AI 配置</p><h3>问答服务</h3></div></div>
                  </template>
                  <el-form label-position="top">
                    <el-form-item label="provider"><el-input v-model.trim="aiForm.provider" /></el-form-item>
                    <el-form-item label="model"><el-input v-model.trim="aiForm.model" /></el-form-item>
                    <el-form-item label="api_base"><el-input v-model.trim="aiForm.api_base" /></el-form-item>
                    <el-form-item :label="`api_key（当前：${adminOverview?.ai_config?.api_key_masked || '未配置'}）`"><el-input v-model="aiForm.api_key" type="password" show-password autocomplete="off" /></el-form-item>
                    <el-form-item label="temperature"><el-input-number v-model="aiForm.temperature" :min="0" :max="1.5" :step="0.1" /></el-form-item>
                    <el-button type="primary" :loading="adminLoading" @click="saveAiConfig">保存配置</el-button>
                  </el-form>
                </el-card>
              </el-col>

              <el-col :xs="24" :lg="14">
                <el-card shadow="never" class="panel-card block-gap">
                  <template #header>
                    <div class="head-row"><div><p class="eyebrow">账号管理</p><h3>创建账号</h3></div></div>
                  </template>
                  <el-form label-position="top">
                    <el-form-item label="昵称"><el-input v-model.trim="createForm.display_name" autocomplete="off" /></el-form-item>
                    <el-form-item label="用户名"><el-input v-model.trim="createForm.username" autocomplete="off" /></el-form-item>
                    <el-form-item label="密码"><el-input v-model="createForm.password" type="password" show-password autocomplete="new-password" /></el-form-item>
                    <el-form-item label="角色">
                      <el-select v-model="createForm.role">
                        <el-option label="普通用户" value="user" />
                        <el-option label="管理员" value="admin" />
                      </el-select>
                    </el-form-item>
                    <el-button type="primary" :loading="adminLoading" @click="createUser">创建账号</el-button>
                  </el-form>
                </el-card>

                <el-card shadow="never" class="panel-card">
                  <template #header>
                    <div class="head-row"><div><p class="eyebrow">账号列表</p><h3>最近账号</h3></div></div>
                  </template>
                  <el-table :data="adminOverview?.users || []" stripe>
                    <el-table-column prop="display_name" label="昵称" min-width="120" />
                    <el-table-column prop="username" label="用户名" min-width="140" />
                    <el-table-column prop="role" label="角色" width="100" />
                    <el-table-column label="操作" width="120">
                      <template #default="scope">
                        <el-button v-if="scope.row.id !== currentUser?.id" type="danger" plain size="small" @click="deleteUser(scope.row.id)">删除</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-card>
              </el-col>
            </el-row>

          </section>
        </div>
      </el-main>
    </el-container>

    <nav v-if="isMobile" class="mobile-tabbar">
      <button
        v-for="item in mobileTabs"
        :key="item.screen"
        type="button"
        class="mobile-tab"
        :class="{ active: currentGroup === item.screen, main: item.screen === 'identify' }"
        @click="handleMobileTab(item.screen)"
      >
        <span class="mobile-icon">
          <span v-if="item.screen === 'identify'" class="flower-icon">
            <span class="petal petal-a"></span>
            <span class="petal petal-b"></span>
            <span class="petal petal-c"></span>
            <span class="petal petal-d"></span>
            <span class="petal petal-e"></span>
          </span>
          <el-icon v-else><component :is="item.icon" /></el-icon>
        </span>
        <span class="mobile-label">{{ item.label }}</span>
      </button>
    </nav>

    <input
      id="gallery-picker"
      ref="galleryInput"
      class="visually-hidden-input"
      type="file"
      accept="image/*"
      @change="onFilePicked($event, 'image')"
    >
    <input
      id="camera-picker"
      ref="cameraInput"
      class="visually-hidden-input"
      type="file"
      accept="image/*"
      capture="environment"
      @change="onFilePicked($event, 'image_camera')"
    >
    <input
      id="avatar-picker"
      ref="avatarInput"
      class="visually-hidden-input"
      type="file"
      accept="image/*"
      @change="onAvatarPicked"
    >
    <input
      id="post-image-picker"
      ref="postImageInput"
      class="visually-hidden-input"
      type="file"
      accept="image/*"
      @change="onPostImagePicked"
    >

    <el-dialog v-model="postDialogVisible" title="我也发一张" width="min(92vw, 560px)" destroy-on-close>
      <div class="post-form-grid">
        <el-input
          v-model="postForm.content"
          type="textarea"
          :rows="4"
          resize="none"
          placeholder="写下这次观察到的线索、环境或判断依据"
        />
        <el-input v-model="postForm.tag_label" maxlength="12" placeholder="动态标签，例如：样区记录" />
        <div class="action-row block-gap-sm">
          <el-button plain @click="postImageInput?.click()">选一张图</el-button>
          <span v-if="postForm.image_name" class="muted">{{ postForm.image_name }}</span>
        </div>
        <div v-if="postImagePreview" class="post-image-preview">
          <img :src="postImagePreview" alt="动态预览">
        </div>
      </div>
      <template #footer>
        <div class="action-row">
          <el-button @click="closePostComposer">取消</el-button>
          <el-button type="primary" :loading="postLoading" @click="submitPost">发布动态</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { insectTaxonomyData, taxonomyGroupOptions } from './insectTaxonomyData'
import { taxonomyDirectoryMap } from './insectTaxonomyTree'
import { taxonomySpeciesSupplement } from './taxonomySpeciesSupplement'
import { taxonomySpeciesImages } from './taxonomySpeciesImages'
import {
  CameraFilled,
  HomeFilled,
  LocationFilled,
  Management,
  MoreFilled,
  Picture,
  Plus,
  Refresh,
  Search,
  UploadFilled,
  User,
} from '@element-plus/icons-vue'

const api = axios.create({ baseURL: '/api', withCredentials: true })
const taxonomyAssetModules = import.meta.glob('./assets/insect-taxonomy/*', { eager: true, import: 'default' })
const taxonomyAssetMap = Object.fromEntries(
  Object.entries(taxonomyAssetModules).map(([path, url]) => [path.split('/').pop(), url]),
)

const homeTabs = [
  { key: 'feed', label: '动态' },
  { key: 'article', label: '文章' },
  { key: 'catalog', label: '百科' },
]

const researchHighlights = [
  {
    id: 'ref-bee',
    tag: '资料补充',
    title: '蜜蜂会综合利用花色、气味和空间方位完成采集',
    summary: '公开资料显示，蜜蜂的采集活动并不只依赖颜色，气味线索和方向判断同样重要，这也是观察授粉昆虫活动带时的重要参考。',
    author: 'Britannica / 平台整理',
    meta: '授粉观察',
    imageIndex: 0,
    kind: 'article',
    url: 'https://www.britannica.com/animal/bee',
  },
  {
    id: 'ref-butterfly',
    tag: '资料补充',
    title: '蝶类的伪装效果往往由纹理与停驻姿态共同构成',
    summary: '蝴蝶与背景之间是否融洽，往往取决于翅面纹理、边缘轮廓和停驻角度，而不只是颜色接近与否。',
    author: 'Britannica / 平台整理',
    meta: '拟态识别',
    imageIndex: 1,
    kind: 'article',
    url: 'https://www.britannica.com/animal/butterfly-insect',
  },
  {
    id: 'ref-cicada',
    tag: '资料补充',
    title: '蝉类的大部分生命周期往往发生在地下阶段',
    summary: '公开自然资料普遍指出，许多蝉类幼期在地下生活较长时间，因此地面观测具有明显的季节性与区域性。',
    author: 'National Geographic / 平台整理',
    meta: '季节监测',
    imageIndex: 2,
    kind: 'article',
    url: 'https://www.nationalgeographic.com/animals/invertebrates/facts/cicadas/',
  },
  {
    id: 'ref-katydid',
    tag: '资料补充',
    title: '纺织娘的识别关键常常落在触角长度与体态方向',
    summary: '在叶片背景中，纺织娘并不是只靠绿色完成拟态，更关键的往往是超长触角、体型比例和停驻方向。',
    author: 'Britannica / 平台整理',
    meta: '结构线索',
    imageIndex: 3,
    kind: 'article',
    url: 'https://www.britannica.com/animal/long-horned-grasshopper',
  },
]

const emptyState = () => ({
  sample_cards: [],
  history_entries: [],
  feed_posts: [],
  user_posts: [],
  article_library: [],
  catalog_cards: [],
  assistant_quick_questions: [],
  result: null,
  current_record_id: null,
  has_result: false,
  error: null,
  current_user: null,
  assistant_state: { enabled: false },
  admin_overview: null,
})

const boot = reactive(emptyState())
const screen = ref('home')
const pageLoading = ref(false)
const analyzeLoading = ref(false)
const authLoading = ref(false)
const adminLoading = ref(false)
const assistantLoading = ref(false)
const authTab = ref('login')
const homeTab = ref('feed')
const taxonomyGroup = ref('all')
const taxonomyQuery = ref('')
const preview = ref('')
const previewName = ref('')
const assistantQuestion = ref('')
const assistantAnswer = ref('')
const viewportWidth = ref(typeof window === 'undefined' ? 1280 : window.innerWidth)
const galleryInput = ref(null)
const cameraInput = ref(null)
const avatarInput = ref(null)
const postImageInput = ref(null)
const postDialogVisible = ref(false)
const postLoading = ref(false)
const postImagePreview = ref('')

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ display_name: '', username: '', password: '' })
const adminLoginForm = reactive({ username: '', password: '' })
const createForm = reactive({ display_name: '', username: '', password: '', role: 'user' })
const postForm = reactive({
  content: '',
  tag_label: '观察动态',
  image_file: null,
  image_name: '',
})
const aiForm = reactive({
  provider: 'deepseek',
  model: 'deepseek-chat',
  api_base: 'https://api.deepseek.com/chat/completions',
  api_key: '',
  temperature: 0.4,
})

const metaMap = {
  home: { kicker: '内容总览', title: '首页', desc: '集中查看样区动态、识别文章与类群图鉴。' },
  taxonomy: { kicker: '昆虫纲图鉴', title: '分类图鉴', desc: '按目级分类浏览昆虫纲主要类群，支持搜索代表类群与代表物种。' },
  identify: { kicker: '图像识别', title: '识别中心', desc: '上传图片后自动进入识别流程与结果页。' },
  result: { kicker: '识别结果', title: '结果与分析', desc: '' },
  mine: { kicker: '账号中心', title: '我的', desc: '统一管理登录、注册和个人识别历史。' },
  admin: { kicker: '管理后台', title: '管理员控制台', desc: '集中维护账号、数据库概览与 DeepSeek 配置。' },
}

const isMobile = computed(() => viewportWidth.value < 980)
const currentUser = computed(() => boot.current_user)
const isAdmin = computed(() => currentUser.value?.role === 'admin')
const samples = computed(() => boot.sample_cards || [])
const history = computed(() => boot.history_entries || [])
const result = computed(() => boot.result)
const recordId = computed(() => boot.current_record_id)
const processImages = computed(() => result.value?.segmentation?.images || [])
const evidenceImages = computed(() => result.value?.classification?.evidence_images || [])
const metrics = computed(() => result.value?.classification?.metrics || [])
const processPreview = computed(() => processImages.value.map((item) => item.src))
const evidencePreview = computed(() => evidenceImages.value.map((item) => item.src))
const meta = computed(() => metaMap[screen.value] || metaMap.home)
const currentGroup = computed(() => {
  if (screen.value === 'result' || screen.value === 'identify') return 'identify'
  if (screen.value === 'admin') return 'mine'
  return screen.value
})
const assistantEnabled = computed(() => Boolean(boot.assistant_state?.enabled))
const adminOverview = computed(() => boot.admin_overview)
const quickQuestions = computed(() => boot.assistant_quick_questions?.length ? boot.assistant_quick_questions : ['它属于害虫还是益虫？'])
const beeAvatar = computed(() => samples.value.find((item) => item.key === 'bee')?.image_url || pickSampleImage(0))
const currentUserAvatar = computed(() => currentUser.value?.avatar_src || beeAvatar.value)

const navItems = computed(() => {
  const items = [
    { screen: 'home', label: '首页', icon: HomeFilled },
    { screen: 'taxonomy', label: '分类图鉴', icon: Picture },
    { screen: 'identify', label: '识别中心', icon: CameraFilled },
    { screen: 'mine', label: '我的', icon: User },
  ]
  if (isAdmin.value) items.push({ screen: 'admin', label: '管理员后台', icon: Management })
  return items
})

const mobileTabs = computed(() => [
  { screen: 'home', label: '首页', icon: HomeFilled },
  { screen: 'taxonomy', label: '图鉴', icon: Picture },
  { screen: 'identify', label: '识别', icon: CameraFilled },
  { screen: 'mine', label: '我的', icon: User },
])

const encyclopediaLinks = {
  bee: 'https://www.britannica.com/animal/bee',
  butterfly: 'https://www.britannica.com/animal/butterfly-insect',
  cicada: 'https://www.nationalgeographic.com/animals/invertebrates/facts/cicadas/',
  dragonfly: 'https://www.britannica.com/animal/dragonfly',
  katydid: 'https://www.britannica.com/animal/long-horned-grasshopper',
  mantis: 'https://www.nationalgeographic.com/animals/invertebrates/facts/praying-mantis',
  antlion: 'https://www.britannica.com/animal/antlion',
  phyllium: 'https://www.britannica.com/animal/leaf-insect',
  stick_insect: 'https://animals.sandiegozoo.org/animals/stick-insect',
  moth: 'https://www.britannica.com/video/258692/moth-versus-butterfly-order-lepidoptera-video',
}

function pickSampleImage(index = 0) {
  if (!samples.value.length) return '/fafu.jpg'
  return samples.value[index % samples.value.length].image_url
}

function resolveTaxonomyAsset(path) {
  const filename = String(path || '').split('/').pop()
  return taxonomyAssetMap[filename] || path
}

function buildFallbackTaxonomyFamilies(order) {
  return [
    {
      id: `${order.id}-group`,
      family_cn: order.focus_cn,
      family_en: order.focus_en,
      family_latin: order.focus_latin,
      summary: order.summary,
      cover_image: order.focus_image,
      species: order.species || [],
    },
  ]
}

function defaultTaxonomyUrl(item) {
  const keyword = item.latin || item.name_en || item.name_cn || ''
  return keyword ? `https://www.google.com/search?q=${encodeURIComponent(keyword)}` : ''
}

function normalizeTaxonomyFamilies(order) {
  const families = (taxonomyDirectoryMap[order.id]?.length ? taxonomyDirectoryMap[order.id] : buildFallbackTaxonomyFamilies(order)).map((family, familyIndex) => {
    const supplement = taxonomySpeciesSupplement[family.id] || []
    const mergedSpecies = [...(family.species || []), ...supplement]
    const dedupedSpecies = Array.from(
      new Map(mergedSpecies.map((item, index) => [item.latin || `${family.id}-${index}`, item])).values(),
    )
    return {
      ...family,
      id: family.id || `${order.id}-family-${familyIndex}`,
      cover_image: resolveTaxonomyAsset(family.cover_image || order.focus_image),
      species: dedupedSpecies.map((item, speciesIndex) => {
        const externalAsset = taxonomySpeciesImages[item.latin] || {}
        const resolvedImage = item.image
          ? resolveTaxonomyAsset(item.image)
          : (externalAsset.image ? resolveTaxonomyAsset(externalAsset.image) : '')
        return {
          ...item,
          id: item.id || `${order.id}-${family.id || familyIndex}-${item.latin || speciesIndex}`,
          image: resolvedImage,
          image_is_generic: !resolvedImage,
          url: item.url || externalAsset.url || defaultTaxonomyUrl(item),
        }
      }),
    }
  })
  return families
}

function buildFeedTitle(content) {
  const text = String(content || '').replace(/\s+/g, ' ').trim()
  return text.length > 18 ? `${text.slice(0, 18)}...` : text
}

const homeFeedItems = computed(() =>
  (boot.feed_posts || []).map((item, index) => ({
    id: item.id ?? `feed-${index}`,
    tag: item.tag_label || '观察动态',
    title: buildFeedTitle(item.content),
    summary: item.content,
    author: item.author?.display_name || item.author || '样区观察',
    meta: item.created_at || '最新更新',
    image_url: item.image_src || pickSampleImage(index),
    record_id: item.record_id || null,
    kind: 'post',
    author_avatar: item.author?.avatar_src || beeAvatar.value,
    kicker: item.tag_label || '观察动态',
  })),
)

const userPosts = computed(() =>
  (boot.user_posts || []).map((item, index) => ({
    id: item.id ?? `user-post-${index}`,
    tag: item.tag_label || '观察动态',
    title: buildFeedTitle(item.content),
    summary: item.content,
    meta: item.created_at || '刚刚发布',
    image_src: item.image_src || '',
    author_avatar: item.author?.avatar_src || currentUserAvatar.value,
  })),
)

const articleItems = computed(() =>
  (boot.article_library || []).map((item, index) => ({
    id: `article-${index}`,
    tag: item.category || '论文精读',
    title: item.title,
    summary: item.summary,
    author: item.source || '期刊论文',
    meta: item.meta || '公开论文',
    image_url: pickSampleImage(index + 2),
    kind: 'article',
    kicker: item.category || '论文精读',
    url: item.url || `https://www.google.com/search?q=${encodeURIComponent(item.title)}`,
  })),
)

const encyclopediaItems = computed(() =>
  (boot.catalog_cards || []).map((item) => ({
    key: item.key,
    tag: '图鉴',
    title: item.title,
    summary: item.clue || item.role,
    author: item.subtitle,
    meta: item.role,
    image_url: item.image_url,
    kind: 'catalog',
    kicker: '图鉴',
    url: encyclopediaLinks[item.key] || `https://www.baidu.com/s?wd=${encodeURIComponent(item.title)}`,
  })),
)

const taxonomyOrders = computed(() => {
  const query = taxonomyQuery.value.trim().toLowerCase()
  return insectTaxonomyData
    .map((order) => {
      const families = normalizeTaxonomyFamilies(order)
      const species = families.flatMap((family) => family.species)
      return {
        ...order,
        focus_image: resolveTaxonomyAsset(order.focus_image),
        families,
        species,
        subgroup_count: families.length,
        species_count: species.length,
      }
    })
    .filter((order) => {
      if (taxonomyGroup.value !== 'all' && order.group !== taxonomyGroup.value) return false
      if (!query) return true
      const haystack = [
        order.order_cn,
        order.order_en,
        order.order_latin,
        order.focus_cn,
        order.focus_en,
        order.focus_latin,
        order.summary,
        ...order.families.flatMap((family) => [
          family.family_cn,
          family.family_en,
          family.family_latin,
          family.summary,
          ...family.species.flatMap((item) => [item.name_cn, item.name_en, item.latin]),
        ]),
      ]
        .join(' ')
        .toLowerCase()
      return haystack.includes(query)
    })
})

const currentHomeItems = computed(() => {
  if (homeTab.value === 'article') return articleItems.value
  if (homeTab.value === 'catalog') return encyclopediaItems.value
  return homeFeedItems.value
})

const desktopHomePosts = computed(() => homeFeedItems.value.slice(0, 4))
const desktopArticles = computed(() => articleItems.value.slice(0, 4))
const desktopCatalog = computed(() => encyclopediaItems.value.slice(0, 4))
const homeHero = computed(() => currentHomeItems.value[0] || {
  kicker: '观察精选',
  title: '样区记录持续更新',
  summary: '上传图片或查看首页内容流，可快速进入识别与比对流程。',
  image_url: pickSampleImage(0),
})
const showcaseHeadline = computed(() => {
  if (homeTab.value === 'article') {
    return {
      kicker: '论文精读',
      title: '真实昆虫论文精选',
      summary: '文章区现在直接引用真实论文与期刊页面，点击卡片就能跳转到原文入口，方便课堂展示、方法对照和论文延读。',
    }
  }
  if (homeTab.value === 'catalog') {
    return {
      kicker: '图鉴卷轴',
      title: '昆虫封面长廊',
      summary: '把 11 类样例做成循环滚动的封面带，在同一个展示框里连续浏览拟态、轮廓和背景差异，点击任一封面可直接跑样例识别。',
    }
  }
  return {
    kicker: '样区精选',
    title: '昆虫展示',
    summary: 'hello,stan',
  }
})
const showcaseRail = computed(() => {
  const cards = samples.value.slice(0, 11)
  return cards.length ? [...cards, ...cards] : []
})
const mobileLocationText = computed(() => `校园样区 · 已更新 ${homeFeedItems.value.length} 条观察`)

function applyBootstrap(payload) {
  Object.assign(boot, emptyState(), payload)
  if (payload?.admin_overview?.ai_config) {
    aiForm.provider = payload.admin_overview.ai_config.provider || 'deepseek'
    aiForm.model = payload.admin_overview.ai_config.model || 'deepseek-chat'
    aiForm.api_base = payload.admin_overview.ai_config.api_base || 'https://api.deepseek.com/chat/completions'
    aiForm.temperature = Number(payload.admin_overview.ai_config.temperature ?? 0.4)
    aiForm.api_key = ''
  }
}

function normalizeScreen(target) {
  const fallback = 'home'
  if (!target) return fallback
  if (target === 'history') return 'mine'
  if (target === 'admin' && !isAdmin.value) return currentUser.value ? 'mine' : fallback
  if (target === 'result' && !result.value && !boot.has_result) return fallback
  return target
}

function syncUrl(target, currentRecord = null) {
  const url = new URL(window.location.href)
  url.searchParams.delete('screen')
  url.searchParams.delete('record_id')
  if (target && target !== 'home') url.searchParams.set('screen', target)
  if (target === 'result' && currentRecord) url.searchParams.set('record_id', String(currentRecord))
  window.history.replaceState({}, '', url)
}

async function loadBootstrap(target = screen.value, currentRecord = null) {
  pageLoading.value = true
  try {
    const params = { _ts: Date.now() }
    if (target) params.screen = target
    if (currentRecord) params.record_id = currentRecord
    const { data } = await api.get('/bootstrap', {
      params,
      headers: { 'Cache-Control': 'no-cache' },
    })
    applyBootstrap(data)
    screen.value = normalizeScreen(target || data.initial_screen || screen.value)
    syncUrl(screen.value, screen.value === 'result' ? data.current_record_id : null)
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '页面数据加载失败')
  } finally {
    pageLoading.value = false
  }
}

function openScreen(target) {
  screen.value = normalizeScreen(target)
  syncUrl(screen.value, screen.value === 'result' ? recordId.value : null)
}

function openResult(targetRecordId) {
  loadBootstrap('result', targetRecordId)
}

function pick(kind) {
  if (screen.value !== 'identify') {
    screen.value = normalizeScreen('identify')
    syncUrl(screen.value, null)
  }
  if (kind === 'camera') return cameraInput.value?.click()
  galleryInput.value?.click()
}

function setPreview(file) {
  if (preview.value) URL.revokeObjectURL(preview.value)
  preview.value = URL.createObjectURL(file)
  previewName.value = file.name || '待识别图片'
}

function resetPostComposer() {
  postForm.content = ''
  postForm.tag_label = '观察动态'
  postForm.image_file = null
  postForm.image_name = ''
  if (postImagePreview.value) {
    URL.revokeObjectURL(postImagePreview.value)
    postImagePreview.value = ''
  }
}

function closePostComposer() {
  postDialogVisible.value = false
  resetPostComposer()
}

function openPostComposer() {
  if (!currentUser.value || currentUser.value.role !== 'user') {
    authTab.value = 'login'
    openScreen('mine')
    ElMessage.warning('请先登录普通用户账号后再发布动态')
    return
  }
  resetPostComposer()
  postDialogVisible.value = true
}

async function onFilePicked(event, fieldName) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  setPreview(file)
  await analyzeFile(file, fieldName)
}

async function analyzeFile(file, fieldName = 'image') {
  analyzeLoading.value = true
  try {
    const form = new FormData()
    form.append(fieldName, file)
    const { data } = await api.post('/analyze', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('识别完成')
    await loadBootstrap('result', data.record_id)
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '识别失败')
  } finally {
    analyzeLoading.value = false
  }
}

async function runSample(key) {
  analyzeLoading.value = true
  try {
    const { data } = await api.get(`/sample/${key}/analyze`)
    ElMessage.success('样例识别完成')
    await loadBootstrap('result', data.record_id)
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '样例识别失败')
  } finally {
    analyzeLoading.value = false
  }
}

function onPostImagePicked(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  postForm.image_file = file
  postForm.image_name = file.name || '动态图片'
  if (postImagePreview.value) URL.revokeObjectURL(postImagePreview.value)
  postImagePreview.value = URL.createObjectURL(file)
}

async function submitPost() {
  const content = String(postForm.content || '').trim()
  if (!content && !postForm.image_file) {
    ElMessage.warning('写两句观察说明，或者至少上传一张图片')
    return
  }

  postLoading.value = true
  try {
    const form = new FormData()
    form.append('content', content)
    form.append('tag_label', String(postForm.tag_label || '').trim() || '观察动态')
    if (postForm.image_file) form.append('image', postForm.image_file)
    await api.post('/posts', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('动态发布成功')
    closePostComposer()
    await loadBootstrap(screen.value === 'mine' ? 'mine' : 'home')
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '动态发布失败')
  } finally {
    postLoading.value = false
  }
}

async function removePost(postId) {
  try {
    await ElMessageBox.confirm('删除后，这条动态将无法恢复。', '确认删除', {
      type: 'warning',
      confirmButtonText: '删除动态',
      cancelButtonText: '取消',
    })
    await api.post(`/posts/${postId}/delete`)
    ElMessage.success('动态已删除')
    await loadBootstrap(screen.value === 'mine' ? 'mine' : 'home')
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error?.response?.data?.error || '删除失败')
  }
}

async function onAvatarPicked(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  try {
    const form = new FormData()
    form.append('avatar', file)
    await api.post('/account/avatar', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('头像更新成功')
    await loadBootstrap('mine')
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '头像上传失败')
  }
}

async function loginUser() {
  if (!loginForm.username || !loginForm.password) return ElMessage.warning('请输入用户名和密码')
  authLoading.value = true
  try {
    await api.post('/auth/login', { ...loginForm, login_scope: 'user-only' })
    loginForm.username = ''
    loginForm.password = ''
    ElMessage.success('登录成功')
    await loadBootstrap('mine')
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '登录失败')
  } finally {
    authLoading.value = false
  }
}

async function registerUser() {
  if (!registerForm.display_name || !registerForm.username || !registerForm.password) return ElMessage.warning('请完整填写注册信息')
  authLoading.value = true
  try {
    await api.post('/auth/register', { ...registerForm })
    registerForm.display_name = ''
    registerForm.username = ''
    registerForm.password = ''
    ElMessage.success('账号创建成功')
    await loadBootstrap('mine')
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '注册失败')
  } finally {
    authLoading.value = false
  }
}

async function loginAdmin() {
  if (!adminLoginForm.username || !adminLoginForm.password) return ElMessage.warning('请输入管理员用户名和密码')
  authLoading.value = true
  try {
    await api.post('/auth/login', { ...adminLoginForm })
    adminLoginForm.username = ''
    adminLoginForm.password = ''
    ElMessage.success('管理员登录成功')
    await loadBootstrap('admin')
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '登录失败')
  } finally {
    authLoading.value = false
  }
}

async function logout() {
  try {
    await api.post('/auth/logout')
    assistantAnswer.value = ''
    ElMessage.success('已退出登录')
    await loadBootstrap('mine')
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '退出失败')
  }
}

async function removeAccount() {
  try {
    await ElMessageBox.confirm('删除账号后，当前账号下的识别记录会一并移除。', '确认删除', {
      type: 'warning',
      confirmButtonText: '删除账号',
      cancelButtonText: '取消',
    })
    await api.post('/account/delete')
    ElMessage.success('账号已删除')
    await loadBootstrap('mine')
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error?.response?.data?.error || '删除失败')
  }
}

async function removeHistory(targetRecordId) {
  try {
    await ElMessageBox.confirm('删除后，该条识别记录将无法恢复。', '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await api.post(`/history/${targetRecordId}/delete`)
    ElMessage.success('记录已删除')
    await loadBootstrap(screen.value === 'result' ? 'mine' : screen.value)
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error?.response?.data?.error || '删除失败')
  }
}

async function askAssistant() {
  if (!assistantQuestion.value.trim()) return ElMessage.warning('请输入想继续了解的问题')
  assistantLoading.value = true
  try {
    const { data } = await api.post('/assistant/ask', { question: assistantQuestion.value, record_id: recordId.value })
    assistantAnswer.value = data.answer
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '问答调用失败')
  } finally {
    assistantLoading.value = false
  }
}

async function createUser() {
  if (!createForm.display_name || !createForm.username || !createForm.password) return ElMessage.warning('请完整填写账号信息')
  adminLoading.value = true
  try {
    await api.post('/admin/users', { ...createForm })
    createForm.display_name = ''
    createForm.username = ''
    createForm.password = ''
    createForm.role = 'user'
    ElMessage.success('账号创建成功')
    await loadBootstrap('admin')
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '创建失败')
  } finally {
    adminLoading.value = false
  }
}

async function deleteUser(userId) {
  try {
    await ElMessageBox.confirm('删除账号后，该用户的识别记录和相关数据会一并清理。', '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await api.post(`/admin/users/${userId}/delete`)
    ElMessage.success('账号已删除')
    await loadBootstrap('admin')
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error?.response?.data?.error || '删除失败')
  }
}

async function saveAiConfig() {
  adminLoading.value = true
  try {
    await api.post('/admin/ai-config', { ...aiForm })
    aiForm.api_key = ''
    ElMessage.success('AI 配置已保存')
    await loadBootstrap('admin')
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '保存失败')
  } finally {
    adminLoading.value = false
  }
}

function handleHomeCard(item) {
  if (item.url) {
    window.open(item.url, '_blank', 'noopener,noreferrer')
    return
  }
  if (item.kind === 'catalog' && item.key) return runSample(item.key)
  if (item.kind === 'post' && item.record_id) return openResult(item.record_id)
  ElMessage.info(item.summary)
}

function openTaxonomyLink(url) {
  if (!url) return
  window.open(url, '_blank', 'noopener,noreferrer')
}

async function jumpToTaxonomy(orderId, event = null) {
  const rail = document.querySelector('.taxonomy-rail')
  const keepScrollTop = rail?.scrollTop ?? 0
  event?.currentTarget?.blur?.()
  if (screen.value !== 'taxonomy') openScreen('taxonomy')
  await nextTick()
  const target = document.getElementById(`taxonomy-${orderId}`)
  if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  requestAnimationFrame(() => {
    if (rail) rail.scrollTop = keepScrollTop
  })
}

function cycleHomeTab() {
  const currentIndex = homeTabs.findIndex((item) => item.key === homeTab.value)
  const nextIndex = currentIndex >= homeTabs.length - 1 ? 0 : currentIndex + 1
  homeTab.value = homeTabs[nextIndex].key
}

function handleMobileTab(target) {
  openScreen(target)
}

function handleResize() {
  viewportWidth.value = window.innerWidth
}

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  window.addEventListener('resize', handleResize)
  const initialScreen = params.get('screen') || 'home'
  const initialRecordId = params.get('record_id') ? Number(params.get('record_id')) : null
  await loadBootstrap(initialScreen, initialRecordId)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (preview.value) URL.revokeObjectURL(preview.value)
  if (postImagePreview.value) URL.revokeObjectURL(postImagePreview.value)
})
</script>

<style>
:root {
  --bg-main: #f4f7e9;
  --bg-soft: #f7f8ef;
  --bg-card: rgba(255, 253, 247, 0.92);
  --line-soft: rgba(104, 117, 63, 0.14);
  --text-main: #2f3924;
  --text-soft: #6f7b58;
  --brand-green: #556b2f;
  --brand-leaf: #6e8b3d;
  --brand-gold: #c98b2d;
  --brand-brown: #7a5530;
}

body {
  margin: 0;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background:
    radial-gradient(circle at top, rgba(210, 224, 161, 0.32), transparent 36%),
    linear-gradient(180deg, #fbfcf4, #eef3dc 58%, #edf2df);
  color: var(--text-main);
}

.el-button--primary {
  --el-button-bg-color: var(--brand-green);
  --el-button-border-color: var(--brand-green);
  --el-button-hover-bg-color: #627c33;
  --el-button-hover-border-color: #627c33;
  --el-button-active-bg-color: #4c6228;
  --el-button-active-border-color: #4c6228;
}

.app-shell {
  min-height: 100vh;
}

.sidebar {
  padding: 24px 0 24px 24px;
}

.main {
  padding: 24px 24px 112px;
}

.panel,
.panel-card {
  border: 1px solid var(--line-soft);
  border-radius: 28px;
  background: var(--bg-card);
  box-shadow: 0 20px 40px rgba(115, 123, 84, 0.12);
  backdrop-filter: blur(12px);
}

.panel {
  padding: 22px;
}

.panel + .panel {
  margin-top: 18px;
}

.brand-panel {
  background:
    radial-gradient(circle at right top, rgba(206, 151, 66, 0.12), transparent 34%),
    linear-gradient(180deg, rgba(252, 250, 240, 0.96), rgba(245, 249, 233, 0.94));
}

.eyebrow,
.small-label {
  color: var(--brand-leaf);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.eyebrow {
  margin: 0 0 10px;
}

.muted {
  color: var(--text-soft);
  line-height: 1.75;
}

.nav-panel {
  display: grid;
  gap: 8px;
}

.nav-btn {
  width: 100%;
  border: 0;
  border-radius: 18px;
  background: transparent;
  color: #5f6e47;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.nav-btn.active,
.nav-btn:hover {
  background: rgba(110, 139, 61, 0.12);
  color: var(--brand-green);
}

.topbar,
.head-row,
.topbar-actions,
.action-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar {
  justify-content: space-between;
  margin-bottom: 18px;
}

.topbar h1,
.head-row h3,
.hero-copy h3 {
  margin: 0;
}

.head-row {
  justify-content: space-between;
}

.block-gap {
  margin-bottom: 18px;
}

.block-gap-sm {
  margin-top: 16px;
}

.desktop-home-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.desktop-banner-copy {
  max-width: 336px;
  display: grid;
  gap: 14px;
}

.desktop-banner-copy h3,
.desktop-banner-copy p {
  margin: 0;
}

.desktop-banner-side {
  flex: 1;
  min-width: 0;
}

.desktop-feed-grid,
.desktop-side-list,
.sample-grid,
.history-grid,
.metric-grid,
.evidence-grid,
.science-list,
.feed-list,
.quick-question-row {
  display: grid;
  gap: 14px;
}

.desktop-feed-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.desktop-feed-card {
  display: grid;
  grid-template-columns: 128px minmax(0, 1fr);
  gap: 14px;
  border-radius: 20px;
  background: rgba(245, 248, 234, 0.9);
  padding: 12px;
}

.desktop-feed-card img,
.sample-item img,
.feed-card img {
  width: 100%;
  object-fit: cover;
  display: block;
}

.desktop-feed-card img {
  height: 124px;
  border-radius: 16px;
}

.side-list-item {
  border-radius: 18px;
  background: rgba(244, 248, 232, 0.9);
  padding: 14px 16px;
  display: grid;
  gap: 8px;
}

.side-list-item strong {
  display: block;
  margin-bottom: 6px;
}

.side-list-item p {
  margin: 0;
  color: var(--text-soft);
  line-height: 1.7;
}

.side-list-link {
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.side-list-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(115, 123, 84, 0.12);
}

.paper-source {
  color: #7f8968;
  font-size: 12px;
}

.paper-link {
  width: fit-content;
  color: var(--brand-brown);
  font-size: 13px;
  text-decoration: none;
}

.paper-link:hover {
  text-decoration: underline;
}

.mobile-home {
  display: grid;
  gap: 18px;
}

.mobile-home-top,
.mobile-home-actions,
.mobile-home-tabs,
.feed-meta {
  display: flex;
  align-items: center;
}

.mobile-home-top {
  justify-content: space-between;
  gap: 14px;
}

.location-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 252, 245, 0.92);
  border: 1px solid rgba(133, 145, 84, 0.16);
  color: #49563b;
}

.mobile-home-actions {
  gap: 10px;
}

.icon-chip {
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 50%;
  background: rgba(255, 251, 245, 0.94);
  color: var(--brand-brown);
  display: grid;
  place-items: center;
  box-shadow: 0 10px 20px rgba(122, 85, 48, 0.12);
}

.mobile-home-tabs {
  gap: 24px;
  padding: 0 4px;
}

.home-tab {
  border: 0;
  background: transparent;
  color: #98a089;
  padding: 4px 0 10px;
  font-size: 18px;
  position: relative;
}

.home-tab.active {
  color: var(--text-main);
  font-weight: 600;
}

.home-tab.active::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: 0;
  width: 34px;
  height: 3px;
  border-radius: 999px;
  background: var(--brand-brown);
  transform: translateX(-50%);
}

.hero-card {
  position: relative;
  overflow: hidden;
  border-radius: 26px;
  background: linear-gradient(135deg, rgba(85, 107, 47, 0.12), rgba(201, 139, 45, 0.08));
}

.cover-showcase-card {
  display: grid;
  gap: 16px;
  min-height: 208px;
  padding: 18px;
}

.cover-showcase-copy {
  display: grid;
  gap: 10px;
}

.hero-kicker {
  margin: 0;
  color: var(--brand-leaf);
  font-size: 12px;
  letter-spacing: 0.08em;
}

.cover-showcase-copy h3,
.cover-showcase-copy p {
  margin: 0;
}

.cover-showcase-copy p:last-child {
  margin: 0;
  color: #566348;
  line-height: 1.7;
}

.showcase-window {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  padding: 10px 0;
  background:
    radial-gradient(circle at top, rgba(255, 255, 255, 0.42), transparent 42%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.5), rgba(233, 240, 212, 0.46));
  border: 1px solid rgba(122, 133, 78, 0.12);
}

.showcase-window::before,
.showcase-window::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 42px;
  z-index: 1;
  pointer-events: none;
}

.showcase-window::before {
  left: 0;
  background: linear-gradient(90deg, rgba(246, 249, 236, 0.96), rgba(246, 249, 236, 0));
}

.showcase-window::after {
  right: 0;
  background: linear-gradient(270deg, rgba(246, 249, 236, 0.96), rgba(246, 249, 236, 0));
}

.showcase-window-desktop {
  min-height: 170px;
}

.showcase-track {
  display: flex;
  gap: 14px;
  width: max-content;
  padding: 0 14px;
  animation: showcase-marquee 34s linear infinite;
}

.showcase-window:hover .showcase-track {
  animation-play-state: paused;
}

.showcase-slide {
  position: relative;
  width: 168px;
  height: 150px;
  flex: 0 0 168px;
  overflow: hidden;
  border: 0;
  border-radius: 20px;
  padding: 0;
  cursor: pointer;
  background: #dfe8c6;
  box-shadow: 0 14px 28px rgba(92, 103, 66, 0.18);
}

.showcase-slide::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.02), rgba(20, 25, 10, 0.54));
}

.showcase-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.showcase-caption {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  display: grid;
  gap: 4px;
  padding: 14px;
  color: #fff;
  text-align: left;
}

.showcase-caption strong,
.showcase-caption span {
  display: block;
}

.showcase-caption span {
  color: rgba(255, 255, 255, 0.82);
  font-size: 12px;
}

@keyframes showcase-marquee {
  from {
    transform: translateX(0);
  }

  to {
    transform: translateX(-50%);
  }
}

.feed-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 132px;
  gap: 14px;
  border-radius: 24px;
  background: rgba(255, 252, 247, 0.95);
  border: 1px solid rgba(130, 140, 90, 0.12);
  padding: 14px;
}

.feed-card img {
  height: 112px;
  border-radius: 18px;
}

.feed-copy {
  display: grid;
  align-content: space-between;
  gap: 10px;
}

.feed-copy h4,
.feed-copy p {
  margin: 0;
}

.feed-copy p {
  color: var(--text-soft);
  line-height: 1.75;
}

.feed-link {
  width: fit-content;
  color: var(--brand-brown);
  font-size: 13px;
  text-decoration: none;
}

.feed-link:hover {
  text-decoration: underline;
}

.feed-tag {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(110, 139, 61, 0.14);
  color: var(--brand-green);
  font-size: 12px;
}

.feed-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.feed-section-head h3 {
  margin: 4px 0 0;
}

.feed-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #8c947d;
  font-size: 12px;
}

.feed-author {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.feed-author img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  flex: 0 0 24px;
  border: 1px solid rgba(110, 139, 61, 0.18);
}

.taxonomy-panel {
  padding: 18px;
}

.taxonomy-toolbar {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
}

.taxonomy-select {
  width: 168px;
}

.taxonomy-search {
  flex: 1;
}

.taxonomy-layout {
  position: relative;
  display: block;
}

.taxonomy-main {
  display: grid;
  gap: 18px;
  padding-right: 108px;
}

.taxonomy-section {
  scroll-margin-top: 92px;
}

.taxonomy-order-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 10px;
  padding: 2px 0;
  color: #7a7a72;
  font-size: 16px;
  letter-spacing: 0.02em;
  border-bottom: 1px solid rgba(110, 139, 61, 0.12);
}

.taxonomy-order-cn {
  font-weight: 700;
  color: #546046;
}

.taxonomy-order-latin {
  font-size: 15px;
  text-transform: uppercase;
}

.taxonomy-order-meta {
  margin-left: auto;
  font-size: 13px;
  color: #8b917d;
  text-transform: none;
}

.taxonomy-level-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid rgba(110, 139, 61, 0.18);
  background: linear-gradient(180deg, rgba(248, 250, 240, 0.96), rgba(240, 245, 229, 0.92));
  color: #607046;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.taxonomy-level-chip-order {
  border-color: rgba(110, 139, 61, 0.22);
  background: rgba(241, 246, 229, 0.95);
}

.taxonomy-level-chip-family,
.taxonomy-level-chip-species {
  margin-bottom: 2px;
}

.taxonomy-focus-card {
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr);
  gap: 18px;
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 252, 247, 0.96);
  border: 1px solid rgba(130, 140, 90, 0.12);
}

.taxonomy-overview {
  margin-top: 4px;
  border-radius: 24px;
  border: 1px solid rgba(130, 140, 90, 0.12);
  background: rgba(255, 253, 247, 0.92);
  overflow: hidden;
}

.taxonomy-overview-summary {
  list-style: none;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  cursor: pointer;
}

.taxonomy-overview-summary::-webkit-details-marker {
  display: none;
}

.taxonomy-overview-avatar {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  object-fit: cover;
  background: #f4f6ea;
  border: 1px solid rgba(130, 140, 90, 0.14);
  box-shadow: 0 10px 22px rgba(104, 117, 63, 0.12);
}

.taxonomy-overview-summary strong {
  font-size: 20px;
  color: #425230;
}

.taxonomy-overview-summary em {
  color: #697659;
  font-size: 15px;
}

.taxonomy-overview-toggle {
  position: relative;
  margin-left: auto;
  padding-right: 18px;
  color: #667255;
  font-size: 13px;
  font-weight: 600;
}

.taxonomy-overview-toggle::after {
  content: '';
  position: absolute;
  top: 5px;
  right: 0;
  width: 8px;
  height: 8px;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transform: rotate(45deg);
  transition: transform 0.18s ease;
}

.taxonomy-overview[open] .taxonomy-overview-toggle::after {
  transform: rotate(225deg);
  top: 9px;
}

.taxonomy-overview-body {
  position: relative;
  padding: 0 16px 16px;
}

.taxonomy-overview-body::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 12px;
  left: 28px;
  width: 2px;
  background: linear-gradient(180deg, rgba(146, 166, 110, 0.34), rgba(146, 166, 110, 0.08));
  border-radius: 999px;
}

.taxonomy-overview-card {
  position: relative;
  margin: 0 0 16px 0;
}

.taxonomy-overview-card::after {
  content: '';
  position: absolute;
  left: 22px;
  bottom: -10px;
  width: 20px;
  height: 2px;
  background: rgba(146, 166, 110, 0.34);
}

.taxonomy-focus-card img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 18px;
  background: #f4f6ea;
}

.taxonomy-focus-copy {
  display: grid;
  align-content: center;
  gap: 8px;
}

.taxonomy-focus-copy h3,
.taxonomy-focus-copy p,
.taxonomy-focus-copy i {
  margin: 0;
}

.taxonomy-focus-copy h3 {
  font-size: 30px;
  line-height: 1.08;
}

.taxonomy-focus-copy > p:not(.muted),
.taxonomy-focus-copy i {
  font-size: 18px;
}

.taxonomy-focus-copy i {
  color: #4c5a37;
}

.taxonomy-family-list {
  position: relative;
  display: grid;
  gap: 12px;
  margin-top: 0;
  padding-left: 34px;
}

.taxonomy-family-list::before {
  content: '';
  position: absolute;
  top: 4px;
  bottom: 12px;
  left: 11px;
  width: 2px;
  background: linear-gradient(180deg, rgba(146, 166, 110, 0.34), rgba(146, 166, 110, 0.08));
  border-radius: 999px;
}

.taxonomy-family {
  position: relative;
  border-radius: 24px;
  border: 1px solid rgba(130, 140, 90, 0.12);
  background: rgba(255, 253, 247, 0.94);
  overflow: hidden;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease, background 0.18s ease;
}

.taxonomy-family::before {
  content: '';
  position: absolute;
  top: 40px;
  left: -22px;
  width: 22px;
  height: 2px;
  background: rgba(146, 166, 110, 0.34);
}

.taxonomy-family::after {
  content: '';
  position: absolute;
  top: 34px;
  left: -30px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: linear-gradient(180deg, #8da566, #6e8b3d);
  box-shadow: 0 0 0 4px rgba(223, 234, 199, 0.9);
}

.taxonomy-family-summary {
  list-style: none;
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.18s ease;
}

.taxonomy-family-summary::-webkit-details-marker {
  display: none;
}

.taxonomy-family-summary img {
  width: 100%;
  height: 92px;
  object-fit: cover;
  border-radius: 16px;
  background: #f4f6ea;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.taxonomy-family-copy {
  display: grid;
  gap: 6px;
}

.taxonomy-family-copy strong,
.taxonomy-family-copy span,
.taxonomy-family-copy em,
.taxonomy-family-copy p {
  margin: 0;
}

.taxonomy-family-copy strong {
  font-size: 22px;
}

.taxonomy-family-copy span,
.taxonomy-family-copy em {
  font-size: 16px;
}

.taxonomy-family-copy span {
  color: #344028;
}

.taxonomy-family-copy em {
  color: #5d664f;
}

.taxonomy-family-toggle {
  position: relative;
  align-self: start;
  padding-right: 18px;
  color: #667255;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  transition: color 0.18s ease;
}

.taxonomy-family-toggle::after {
  content: '';
  position: absolute;
  top: 5px;
  right: 0;
  width: 8px;
  height: 8px;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transform: rotate(45deg);
  transition: transform 0.18s ease;
}

.taxonomy-family[open] .taxonomy-family-toggle::after {
  transform: rotate(225deg);
  top: 9px;
}

.taxonomy-family[open] {
  border-color: rgba(110, 139, 61, 0.26);
  background: linear-gradient(180deg, rgba(252, 254, 247, 0.98), rgba(246, 250, 237, 0.96));
  box-shadow: 0 18px 36px rgba(104, 117, 63, 0.12);
}

.taxonomy-family[open]::before {
  background: linear-gradient(90deg, rgba(110, 139, 61, 0.76), rgba(161, 188, 118, 0.65));
}

.taxonomy-family[open]::after {
  background: linear-gradient(180deg, #6e8b3d, #4f6c21);
  box-shadow: 0 0 0 5px rgba(222, 235, 191, 0.98), 0 6px 18px rgba(110, 139, 61, 0.22);
}

.taxonomy-family[open] .taxonomy-family-summary {
  background: linear-gradient(180deg, rgba(246, 250, 236, 0.98), rgba(255, 253, 247, 0.9));
}

.taxonomy-family[open] .taxonomy-family-summary img {
  transform: scale(1.02);
  box-shadow: 0 12px 24px rgba(104, 117, 63, 0.14);
}

.taxonomy-family[open] .taxonomy-family-copy strong,
.taxonomy-family[open] .taxonomy-family-toggle {
  color: #4e6423;
}

.taxonomy-family[open] .taxonomy-level-chip-family,
.taxonomy-family[open] .taxonomy-level-chip-species {
  border-color: rgba(110, 139, 61, 0.3);
  background: rgba(241, 246, 229, 0.98);
  color: #566c30;
}

.taxonomy-family-body {
  position: relative;
  margin-left: 26px;
  padding: 0 0 16px 20px;
}

.taxonomy-family-body::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 18px;
  left: 9px;
  width: 2px;
  background: linear-gradient(180deg, rgba(146, 166, 110, 0.28), rgba(146, 166, 110, 0.06));
  border-radius: 999px;
}

.taxonomy-family[open] .taxonomy-family-body::before {
  background: linear-gradient(180deg, rgba(110, 139, 61, 0.58), rgba(110, 139, 61, 0.14));
}

.taxonomy-species-list {
  display: grid;
  gap: 12px;
  margin-top: 0;
}

.taxonomy-species-card {
  position: relative;
  width: 100%;
  border: 0;
  border-radius: 22px;
  padding: 14px 16px;
  background: rgba(255, 253, 247, 0.94);
  border: 1px solid rgba(130, 140, 90, 0.12);
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  gap: 18px;
  align-items: center;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease, background 0.18s ease;
}

.taxonomy-species-card::before {
  content: '';
  position: absolute;
  top: 50%;
  left: -19px;
  width: 19px;
  height: 2px;
  background: rgba(146, 166, 110, 0.28);
  transform: translateY(-50%);
}

.taxonomy-species-card::after {
  content: '';
  position: absolute;
  top: calc(50% - 5px);
  left: -25px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #99af6f;
  box-shadow: 0 0 0 3px rgba(232, 239, 215, 0.92);
}

.taxonomy-family[open] .taxonomy-species-card {
  border-color: rgba(110, 139, 61, 0.18);
  background: rgba(255, 254, 249, 0.98);
}

.taxonomy-family[open] .taxonomy-species-card::before {
  background: linear-gradient(90deg, rgba(110, 139, 61, 0.56), rgba(110, 139, 61, 0.18));
}

.taxonomy-family[open] .taxonomy-species-card::after {
  background: #7f9951;
  box-shadow: 0 0 0 4px rgba(229, 239, 207, 0.96);
}

.taxonomy-family[open] .taxonomy-species-card:hover {
  transform: translateX(3px);
  border-color: rgba(110, 139, 61, 0.28);
  box-shadow: 0 14px 28px rgba(104, 117, 63, 0.12);
}

.taxonomy-species-thumb {
  width: 100%;
  height: 92px;
  border-radius: 16px;
  overflow: hidden;
  background: #f4f6ea;
}

.taxonomy-species-card img,
.taxonomy-species-placeholder {
  width: 100%;
  height: 92px;
  border-radius: 16px;
}

.taxonomy-species-card img {
  object-fit: cover;
  background: #f4f6ea;
}

.taxonomy-species-placeholder {
  display: grid;
  place-items: center;
  gap: 6px;
  padding: 10px;
  color: #73825e;
  background:
    linear-gradient(180deg, rgba(246, 249, 236, 0.96), rgba(236, 242, 221, 0.92)),
    radial-gradient(circle at top, rgba(198, 214, 150, 0.22), transparent 50%);
}

.taxonomy-species-placeholder .el-icon {
  font-size: 22px;
}

.taxonomy-species-placeholder span {
  font-size: 12px;
  font-weight: 600;
}

.taxonomy-species-thumb.is-generic {
  border: 1px dashed rgba(130, 140, 90, 0.22);
}

.taxonomy-species-copy {
  display: grid;
  gap: 6px;
}

.taxonomy-species-copy strong,
.taxonomy-species-copy span,
.taxonomy-species-copy em {
  margin: 0;
}

.taxonomy-species-copy strong {
  font-size: 22px;
}

.taxonomy-species-copy span {
  color: #344028;
  font-size: 18px;
}

.taxonomy-species-copy em {
  color: #5d664f;
  font-size: 17px;
}

.taxonomy-rail {
  position: fixed;
  top: 148px;
  right: 30px;
  z-index: 18;
  width: 82px;
  max-height: calc(100vh - 188px);
  display: grid;
  gap: 10px;
  padding: 14px 10px;
  overflow-y: auto;
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(255, 253, 247, 0.96), rgba(246, 249, 238, 0.94));
  border: 1px solid rgba(130, 140, 90, 0.14);
  box-shadow: 0 16px 30px rgba(104, 117, 63, 0.08);
}

.taxonomy-rail-item {
  border: 1px solid rgba(130, 140, 90, 0.12);
  border-radius: 18px;
  background: rgba(255, 253, 247, 0.94);
  color: #425230;
  display: grid;
  justify-items: center;
  padding: 10px 5px;
  min-height: 64px;
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease, background 0.16s ease;
}

.taxonomy-rail-item:hover {
  transform: translateX(-2px);
  box-shadow: 0 10px 18px rgba(104, 117, 63, 0.12);
  border-color: rgba(110, 139, 61, 0.26);
  background: rgba(246, 250, 236, 0.98);
}

.taxonomy-rail-cn {
  font-size: 14px;
  font-weight: 700;
  writing-mode: vertical-rl;
  text-orientation: upright;
  letter-spacing: 0.08em;
}

.insect-panel {
  background:
    radial-gradient(circle at right top, rgba(201, 139, 45, 0.09), transparent 30%),
    linear-gradient(180deg, rgba(251, 250, 241, 0.96), rgba(246, 249, 236, 0.94));
}

.preview-box {
  margin-top: 18px;
  min-height: 260px;
  border: 1px dashed rgba(110, 139, 61, 0.28);
  border-radius: 24px;
  overflow: hidden;
  background: rgba(247, 249, 238, 0.92);
}

.preview-box img,
.main-image .el-image__inner,
.mini-image .el-image__inner {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.preview-box.empty {
  display: grid;
  place-items: center;
  color: #7c8665;
  text-align: center;
  padding: 24px;
}

.preview-copy {
  padding: 14px 16px;
}

.action-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 20px;
  border-radius: 10px;
  border: 1px solid var(--line-soft);
  background: rgba(255, 253, 247, 0.96);
  color: var(--text-main);
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
}

.action-label:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(115, 123, 84, 0.12);
  border-color: rgba(85, 107, 47, 0.2);
}

.action-label-primary {
  border-color: var(--brand-green);
  background: var(--brand-green);
  color: #fff;
}

.action-label.disabled {
  pointer-events: none;
  opacity: 0.6;
}

.action-label-inner {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.visually-hidden-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}

.sample-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.sample-item {
  width: 100%;
  border: 0;
  border-radius: 18px;
  background: rgba(245, 248, 234, 0.94);
  cursor: pointer;
  display: grid;
  grid-template-columns: 88px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  text-align: left;
  padding: 10px;
}

.sample-item img {
  height: 78px;
  border-radius: 14px;
}

.history-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.history-item {
  display: grid;
  gap: 10px;
}

.history-main {
  grid-template-columns: 128px minmax(0, 1fr);
  padding: 12px;
}

.history-main img {
  height: 100px;
}

.main-image {
  display: block;
  width: 100%;
  min-height: 340px;
  height: clamp(340px, 46vw, 480px);
  border-radius: 22px;
  overflow: hidden;
}

.metric-grid,
.evidence-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.mini-card {
  background: rgba(245, 248, 234, 0.95);
  border-radius: 18px;
  padding: 12px;
}

.mini-card span {
  color: #697553;
  font-size: 13px;
}

.mini-card strong {
  display: block;
  margin-top: 8px;
}

.mini-image {
  display: block;
  width: 100%;
  margin: 10px 0;
  aspect-ratio: 4 / 3;
  border-radius: 14px;
  overflow: hidden;
}

.main-image .el-image__wrapper,
.mini-image .el-image__wrapper {
  width: 100%;
  height: 100%;
}

.science-list p {
  margin: 0;
  line-height: 1.85;
}

.quick-question-row {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-bottom: 14px;
}

.quick-chip {
  border: 0;
  border-radius: 999px;
  background: rgba(110, 139, 61, 0.12);
  color: var(--brand-green);
  padding: 10px 12px;
  text-align: left;
}

.answer-box {
  margin-top: 16px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(245, 248, 234, 0.95);
  color: #546046;
  line-height: 1.8;
  white-space: pre-wrap;
}

.answer-box.empty {
  color: #889076;
}

.profile {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6e8b3d, #c98b2d);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 28px;
  font-weight: 700;
}

.avatar-photo {
  overflow: hidden;
  background: rgba(255, 251, 243, 0.95);
}

.avatar-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-tools {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}




.profile-copy {
  flex: 1;
}

.post-form-grid {
  display: grid;
  gap: 14px;
}

.post-image-preview {
  border-radius: 18px;
  overflow: hidden;
  background: rgba(245, 248, 234, 0.95);
  min-height: 160px;
}

.post-image-preview img {
  width: 100%;
  max-height: 280px;
  object-fit: cover;
  display: block;
}

.post-history-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.post-history-card {
  display: grid;
  gap: 12px;
  align-content: start;
  padding: 14px;
  border-radius: 22px;
  background: rgba(245, 248, 234, 0.95);
  border: 1px solid rgba(130, 140, 90, 0.14);
}

.post-history-media {
  width: 100%;
  height: 180px;
  border-radius: 16px;
  object-fit: cover;
  display: block;
}

.post-history-copy {
  display: grid;
  gap: 8px;
}

.post-history-copy p,
.post-history-copy strong {
  margin: 0;
}

.auth-card {
  max-width: 720px;
}

.auth-title {
  margin-bottom: 18px;
}

.auth-title h3,
.auth-title p {
  margin: 0;
}

.mobile-tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: -20px;
  z-index: 20;
  display: none;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 4px;
  padding-top: 2px;
  padding-right: 12px;
  padding-left: 12px;
  padding-bottom: max(0px, calc(env(safe-area-inset-bottom) - 22px));
  border-radius: 16px 16px 0 0;
  background: rgba(255, 255, 250, 0.96);
  border: 1px solid rgba(122, 133, 78, 0.14);
  border-bottom: 0;
  box-shadow: 0 -4px 14px rgba(94, 100, 69, 0.08);
}

.mobile-tab {
  border: 0;
  background: transparent;
  color: #8f9781;
  display: grid;
  grid-auto-rows: max-content;
  align-content: center;
  justify-items: center;
  gap: 2px;
  padding: 2px 0 4px;
  min-height: auto;
}

.mobile-tab.active {
  color: var(--brand-green);
}

.mobile-tab.main {
  margin-top: 4px;
}

.mobile-icon {
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  font-size: 20px;
}

.mobile-label {
  display: block;
  font-size: 12px;
  line-height: 1.05;
  text-align: center;
}

.mobile-tab.main .mobile-label {
  margin-top: 2px;
}

.mobile-tab.main .mobile-icon {
  width: 44px;
  height: 44px;
}

.flower-icon {
  position: relative;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: block;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 249, 240, 0.94));
  box-shadow: 0 10px 20px rgba(122, 133, 78, 0.22);
}

.petal {
  position: absolute;
  width: 12px;
  height: 18px;
  border-radius: 12px 12px 4px 12px;
  left: 50%;
  top: 50%;
  transform-origin: center 10px;
}

.petal-a { background: linear-gradient(180deg, #ff8a34, #ffbf54); transform: translate(-50%, -68%) rotate(0deg); }
.petal-b { background: linear-gradient(180deg, #f24867, #ff7795); transform: translate(-50%, -68%) rotate(55deg); }
.petal-c { background: linear-gradient(180deg, #a13ce0, #d17bff); transform: translate(-50%, -68%) rotate(112deg); }
.petal-d { background: linear-gradient(180deg, #3f73f1, #6bb8ff); transform: translate(-50%, -68%) rotate(196deg); }
.petal-e { background: linear-gradient(180deg, #43af7a, #7edb9d); transform: translate(-50%, -68%) rotate(252deg); }

.mobile-app .main {
  padding: 18px 18px 50px;
}

@media (max-width: 979px) {
  .topbar,
  .profile {
    flex-direction: column;
    align-items: flex-start;
  }

  .desktop-home-banner {
    flex-direction: column;
    align-items: stretch;
  }

  .sample-grid,
  .history-grid,
  .metric-grid,
  .evidence-grid,
  .quick-question-row {
    grid-template-columns: 1fr;
  }

  .main-image {
    min-height: 220px;
  }

  .mobile-tabbar {
    display: grid;
  }

  .feed-card {
    grid-template-columns: 1fr 122px;
  }

  .feed-card img {
    height: 108px;
  }

  .taxonomy-toolbar,
  .taxonomy-focus-card {
    align-items: stretch;
    grid-template-columns: 1fr;
  }

  .taxonomy-overview-summary {
    flex-wrap: wrap;
  }

  .taxonomy-overview-avatar {
    width: 46px;
    height: 46px;
    border-radius: 16px;
  }

  .taxonomy-overview-toggle {
    margin-left: 0;
  }

  .taxonomy-overview-body {
    padding: 0 12px 12px;
  }

  .taxonomy-overview-body::before {
    left: 18px;
  }

  .taxonomy-order-meta {
    margin-left: 0;
    width: 100%;
  }

  .taxonomy-layout {
    display: block;
  }

  .taxonomy-rail {
    display: none;
  }

  .taxonomy-main {
    padding-right: 0;
  }

  .taxonomy-family-summary {
    grid-template-columns: 92px minmax(0, 1fr);
  }

  .taxonomy-family-summary img {
    height: 82px;
  }

  .taxonomy-family-list {
    padding-left: 22px;
  }

  .taxonomy-family::before {
    left: -16px;
    width: 16px;
  }

  .taxonomy-family::after {
    left: -22px;
  }

  .taxonomy-family-body {
    margin-left: 12px;
    padding-left: 14px;
  }

  .taxonomy-family-body::before {
    left: 5px;
  }

  .taxonomy-family-toggle {
    grid-column: 2;
    justify-self: start;
  }

  .taxonomy-species-card {
    grid-template-columns: 96px minmax(0, 1fr);
    gap: 14px;
  }

  .taxonomy-species-card::before {
    left: -13px;
    width: 13px;
  }

  .taxonomy-species-card::after {
    left: -18px;
  }

  .taxonomy-species-thumb,
  .taxonomy-species-card img,
  .taxonomy-species-placeholder {
    height: 82px;
  }

  .taxonomy-species-copy strong {
    font-size: 18px;
  }

  .taxonomy-species-copy span,
  .taxonomy-species-copy em {
    font-size: 15px;
  }

  .feed-section-head,
  .avatar-tools {
    align-items: flex-start;
    flex-direction: column;
  }

  .post-history-grid {
    grid-template-columns: 1fr;
  }

  .showcase-slide {
    width: 148px;
    height: 132px;
    flex-basis: 148px;
  }
}
</style>
