# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [1.8.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.7.2...1.8.0) (2023-02-20)


### Features

* **ga4:** add sent_to parameter ([5c57ff9](https://github.com/rudderlabs/rudder-config-schema/commit/5c57ff987726967a9e27ccd999f9ed3b1938f2e7))

### [1.7.2](https://github.com/rudderlabs/rudder-config-schema/compare/1.7.1...1.7.2) (2023-02-17)

### [1.7.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.7.0...1.7.1) (2023-02-16)

## [1.7.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.5...1.7.0) (2023-02-14)


### Features

* added support for  both click event and dynamic remarketing events ([#309](https://github.com/rudderlabs/rudder-config-schema/issues/309)) ([2d8a2b4](https://github.com/rudderlabs/rudder-config-schema/commit/2d8a2b420fa97d76565190ebb37b7b462c9de0af))
* adds singer shopify ([98d1057](https://github.com/rudderlabs/rudder-config-schema/commit/98d1057e50c0793ffd23ed7317b98ec14ef13621))
* updates mixpanel image ([d86d0c2](https://github.com/rudderlabs/rudder-config-schema/commit/d86d0c2bccc5644a0f44aab81165f6b76b7aee39))


### Bug Fixes

* **facebook_pixel:** validation inconsistency in ui and schema ([#356](https://github.com/rudderlabs/rudder-config-schema/issues/356)) ([9b4e48d](https://github.com/rudderlabs/rudder-config-schema/commit/9b4e48d2c49aae203b11fef35099b6a2998ce51b))

### [1.6.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.0...1.6.1) (2023-02-03)


### Features

* onboarding Lemnisk device mode ([#326](https://github.com/rudderlabs/rudder-config-schema/issues/326)) ([e64f957](https://github.com/rudderlabs/rudder-config-schema/commit/e64f957d9fd5d4b8d4d7ea75c9be44f172b83f6e))

## [1.6.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.5.0...1.6.0) (2023-02-02)


### Features

* add time window layout to s3 datalake glue ([#348](https://github.com/rudderlabs/rudder-config-schema/issues/348)) ([784bd3f](https://github.com/rudderlabs/rudder-config-schema/commit/784bd3fca1f50899430c544608cee4234cf858e9))
* added catalog for databricks ([#253](https://github.com/rudderlabs/rudder-config-schema/issues/253)) ([#338](https://github.com/rudderlabs/rudder-config-schema/issues/338)) ([56e9bf8](https://github.com/rudderlabs/rudder-config-schema/commit/56e9bf8c5fa76200c0611833673b648d0109fc5c))
* added OneTrust consent support for mobile device modes ([19454ee](https://github.com/rudderlabs/rudder-config-schema/commit/19454ee8b72a8e0d6f7348fbc02ae860323623a4))
* added use rudder storage option to deltalake ([#349](https://github.com/rudderlabs/rudder-config-schema/issues/349)) ([3ad3317](https://github.com/rudderlabs/rudder-config-schema/commit/3ad3317b17e0a5f2b8074c35c3863507d1a6cdd4))
* **CDK v2:** enabling CDK v2 comparison for webhook ([#341](https://github.com/rudderlabs/rudder-config-schema/issues/341)) ([33e59c5](https://github.com/rudderlabs/rudder-config-schema/commit/33e59c5c43334f567689de70e971081df093f661))
* **destination:** onboard criteo audience integration ([#320](https://github.com/rudderlabs/rudder-config-schema/issues/320)) ([fd6fbb6](https://github.com/rudderlabs/rudder-config-schema/commit/fd6fbb61ead9b7a576a9f32326336a302f35a0da))
* **integration:** rockerbox- revert adding support for custom properties ([#345](https://github.com/rudderlabs/rudder-config-schema/issues/345)) ([2de567a](https://github.com/rudderlabs/rudder-config-schema/commit/2de567a37943f1d95621f35b6d58a93f49b99f75))
* **mailchimp:** add support for track call ([#327](https://github.com/rudderlabs/rudder-config-schema/issues/327)) ([16ce89a](https://github.com/rudderlabs/rudder-config-schema/commit/16ce89afa5a6faa76f3877365b524cf46ae1d3e9))
* **optimizely:** add fullstack cloude mode support ([#317](https://github.com/rudderlabs/rudder-config-schema/issues/317)) ([cda7dd5](https://github.com/rudderlabs/rudder-config-schema/commit/cda7dd594cdc4dafc0f3e77b43faa18686347fd0))


### Bug Fixes

* add supportedMessageTypes in GAEC ([#339](https://github.com/rudderlabs/rudder-config-schema/issues/339)) ([8a93e92](https://github.com/rudderlabs/rudder-config-schema/commit/8a93e92276e70268f5e49c0de94cc9553b24ee56))
* add tag option to standard-version command ([fc8264b](https://github.com/rudderlabs/rudder-config-schema/commit/fc8264b543005a6a6ed6e4077d8125a7b9f60480))
* adobe_analytics schema regex ([#325](https://github.com/rudderlabs/rudder-config-schema/issues/325)) ([9751dba](https://github.com/rudderlabs/rudder-config-schema/commit/9751dba7c141e8507edcb452a4da03d13b4b6351))
* default blockPageViewEvent enabled to prevent duplicate page calls ([#340](https://github.com/rudderlabs/rudder-config-schema/issues/340)) ([24f8fcf](https://github.com/rudderlabs/rudder-config-schema/commit/24f8fcfec22cf06849bfed76f08584024c109489))
* optimizely fullstack schema ([#344](https://github.com/rudderlabs/rudder-config-schema/issues/344)) ([e42af44](https://github.com/rudderlabs/rudder-config-schema/commit/e42af44f05ed72c51c590839b635b18e7808e2df))

## [1.5.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.4.1...1.5.0) (2023-01-25)


### Features

* **integration:** rockerbox- add support for custom properties ([#315](https://github.com/rudderlabs/rudder-config-schema/issues/315)) ([a06c9d5](https://github.com/rudderlabs/rudder-config-schema/commit/a06c9d539b9aebef04e85f05515366707c54762a))


### Bug Fixes

* **changelog:** fixing changelog for release 1.4.0, 1.3.7 and 1.3.4 ([#333](https://github.com/rudderlabs/rudder-config-schema/issues/333)) ([b2d5604](https://github.com/rudderlabs/rudder-config-schema/commit/b2d5604abe825c81acab638464b9de224c08a3fb))

### [1.4.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.4.0...1.4.1) (2023-01-24)


### Bug Fixes

* move mp,zendesk,sfmc to processor ([7433e22](https://github.com/rudderlabs/rudder-config-schema/commit/7433e229c1426a7cd5d0aefc2fd94442170b9e45))

## [1.4.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.7...1.4.0) (2023-01-24)


### Features

* **destination:** onboard lemnisk integration ([#306](https://github.com/rudderlabs/rudder-config-schema/issues/306)) ([392a9d1](https://github.com/rudderlabs/rudder-config-schema/commit/392a9d1ae1be9f4046c4eeea0f49b1b9166a5fcd))
* ga4 hybrid mode support ([#316](https://github.com/rudderlabs/rudder-config-schema/issues/316)) ([724e865](https://github.com/rudderlabs/rudder-config-schema/commit/724e86516a8b5d86aefeb3db6da0e54ac1ebc569))
* updated the ui-config of amplitude to version2 ([#318](https://github.com/rudderlabs/rudder-config-schema/issues/318)) ([caa8bf8](https://github.com/rudderlabs/rudder-config-schema/commit/caa8bf8108fe213c6162eb800a2b17e549330925))


### Bug Fixes

* disables skills resource in freshdesk ([f2c7343](https://github.com/rudderlabs/rudder-config-schema/commit/f2c7343bb7c411685c92609d67bffdfd59bc3b64))

### [1.3.7](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.6...1.3.7) (2023-01-18)


### Features

* add axeptio into prod ([#302](https://github.com/rudderlabs/rudder-config-schema/issues/302)) ([231db08](https://github.com/rudderlabs/rudder-config-schema/commit/231db0873b9bd948521d69fa7cc25efdd621a394))
* add microsoft clarity to prod ([#275](https://github.com/rudderlabs/rudder-config-schema/issues/275)) ([9327566](https://github.com/rudderlabs/rudder-config-schema/commit/9327566284652fb48c98da3ca31776661df03e66))
* added catalog for databricks ([#253](https://github.com/rudderlabs/rudder-config-schema/issues/253)) ([#308](https://github.com/rudderlabs/rudder-config-schema/issues/308)) ([4446798](https://github.com/rudderlabs/rudder-config-schema/commit/4446798083cff92760b5dac7ee6b7d2a9939e0c9))
* update footernote in bigquerystream ([#271](https://github.com/rudderlabs/rudder-config-schema/issues/271)) ([4aeaa42](https://github.com/rudderlabs/rudder-config-schema/commit/4aeaa42240d237e784bb8ea397ad69a003573dc4))


### Bug Fixes

* bing ads updated image ([#292](https://github.com/rudderlabs/rudder-config-schema/issues/292)) ([e3891c1](https://github.com/rudderlabs/rudder-config-schema/commit/e3891c1a8ca2567a95e398d1dfbceefa6013edc5))

### [1.3.6](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.5...1.3.6) (2023-01-13)


### Bug Fixes

* reenable ga4 page call support for cloud mode ([#299](https://github.com/rudderlabs/rudder-config-schema/issues/299)) ([8bf3643](https://github.com/rudderlabs/rudder-config-schema/commit/8bf3643c4edd268a562f67f79f4a0b3ea22248d1))

### [1.3.5](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.4...1.3.5) (2023-01-13)


### Bug Fixes

* enanble pro and enterpise for cdkv2 comparison test ([#293](https://github.com/rudderlabs/rudder-config-schema/issues/293)) ([a6593dc](https://github.com/rudderlabs/rudder-config-schema/commit/a6593dcac8f96d2ad925121095ce307a3daabe5a))

### [1.3.4](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.3...1.3.4) (2023-01-13)

### [1.3.3](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.2...1.3.3) (2023-01-13)


### Bug Fixes

* enable cdkv2 for algolia and pinterest ([630644e](https://github.com/rudderlabs/rudder-config-schema/commit/630644e5466d5d624e76f52dd37d1524e71ef499))
* revert a specific commit from [#253](https://github.com/rudderlabs/rudder-config-schema/issues/253) ([#284](https://github.com/rudderlabs/rudder-config-schema/issues/284)) ([856c9b9](https://github.com/rudderlabs/rudder-config-schema/commit/856c9b91c3f33bef5ca8c46b1d0b751629574b8f))

### [1.3.2](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.1...1.3.2) (2023-01-12)


### Bug Fixes

* hotfix intercom image update ([#280](https://github.com/rudderlabs/rudder-config-schema/issues/280)) ([0aeef10](https://github.com/rudderlabs/rudder-config-schema/commit/0aeef10eed47b0715fd878c2753c0c298ab794b3))

### [1.3.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.0...1.3.1) (2023-01-12)


### Bug Fixes

* destination transformation change from processor to router ([#246](https://github.com/rudderlabs/rudder-config-schema/issues/246)) ([2c3b461](https://github.com/rudderlabs/rudder-config-schema/commit/2c3b46186db5e5d286c293a1af644a98f82d2123))

## [1.3.0](https://github.com/rudderlabs/rudder-config-schema/compare/a615d2b76ce7cf7cebb5c1241806b5de3de2f857...1.3.0) (2023-01-12)


### Features

* add config for enabling iam role for streaming destinations ([#121](https://github.com/rudderlabs/rudder-config-schema/issues/121)) ([0ec3a1e](https://github.com/rudderlabs/rudder-config-schema/commit/0ec3a1e79a9c8ed49f45f3f2f60d5783691cf086))
* add validations and made it a node repo ([a615d2b](https://github.com/rudderlabs/rudder-config-schema/commit/a615d2b76ce7cf7cebb5c1241806b5de3de2f857))
* added block pageview toggle ([#264](https://github.com/rudderlabs/rudder-config-schema/issues/264)) ([2f4f48c](https://github.com/rudderlabs/rudder-config-schema/commit/2f4f48c64c6135e1a4abdc693ab78d6cbb12b7c4))
* added Braze dedup support for mobile SDKs ([#242](https://github.com/rudderlabs/rudder-config-schema/issues/242)) ([1912792](https://github.com/rudderlabs/rudder-config-schema/commit/1912792a39dd869ee329d38c0cc938b95d508971))
* added IAM role based configurations for warehouse destinations ([#198](https://github.com/rudderlabs/rudder-config-schema/issues/198)) ([19220d2](https://github.com/rudderlabs/rudder-config-schema/commit/19220d251434821f29712a89f1f7b5800e09f06f))
* added profileId in dest config campaign manager ([#130](https://github.com/rudderlabs/rudder-config-schema/issues/130)) ([f9e641e](https://github.com/rudderlabs/rudder-config-schema/commit/f9e641e7597c3138ab72f39a088ca1f5aee03007))
* added role parameter to snowflake RETL ([f10bb88](https://github.com/rudderlabs/rudder-config-schema/commit/f10bb8882abcce10a1c26a0f9b5a9bbf1d836b91))
* added singer-freshdesk ([8958966](https://github.com/rudderlabs/rudder-config-schema/commit/89589660fdd3824f655133442e4a9978929d1dc6))
* added singer-freshdesk ([a2fbad6](https://github.com/rudderlabs/rudder-config-schema/commit/a2fbad63a7ab5ba7760eb18738bbc08985133c6b))
* **algolia:** configure cdk v2 threshold ([#70](https://github.com/rudderlabs/rudder-config-schema/issues/70)) ([b964439](https://github.com/rudderlabs/rudder-config-schema/commit/b964439db84bbd6008245ecd15518df030df0e3c))
* allow usage of OneTrust category ids or names ([#237](https://github.com/rudderlabs/rudder-config-schema/issues/237)) ([4892d4e](https://github.com/rudderlabs/rudder-config-schema/commit/4892d4eee308b8fdb8bad8bb062b01f37b1ad8b9))
* **braze:** braze logs feat ([#251](https://github.com/rudderlabs/rudder-config-schema/issues/251)) ([5758d23](https://github.com/rudderlabs/rudder-config-schema/commit/5758d2343fd2abe0eb1c63fdfe633c495ff5b51d))
* **braze:** braze logs feat ([#254](https://github.com/rudderlabs/rudder-config-schema/issues/254)) ([7e8cc34](https://github.com/rudderlabs/rudder-config-schema/commit/7e8cc349640e835d05e9eb383fd4e95c13e1d7e0))
* **braze:** braze logs flag ([#252](https://github.com/rudderlabs/rudder-config-schema/issues/252)) ([c2f8017](https://github.com/rudderlabs/rudder-config-schema/commit/c2f80170113a9f91d9789903fdee7ed7335068b5))
* **braze:** make logs visibility configurable braze ([#240](https://github.com/rudderlabs/rudder-config-schema/issues/240)) ([c052a6d](https://github.com/rudderlabs/rudder-config-schema/commit/c052a6d885eb8f773596900fcbf43b61c270271b))
* **dcm floodlight:** add iframe support ([#61](https://github.com/rudderlabs/rudder-config-schema/issues/61)) ([e1804c0](https://github.com/rudderlabs/rudder-config-schema/commit/e1804c0dcc28fbf1a6db4a37cb8e17a627bb37fa))
* **dcm floodlight:** add iframe support ([#80](https://github.com/rudderlabs/rudder-config-schema/issues/80)) ([559fbaa](https://github.com/rudderlabs/rudder-config-schema/commit/559fbaaa273c080bf227bbb1333cdaa524255b53))
* deploying singer freshdesk ([7aac54c](https://github.com/rudderlabs/rudder-config-schema/commit/7aac54caf4f5def3f9be4e477cffaf0359070407))
* **destination:** onboard awin integration ([#140](https://github.com/rudderlabs/rudder-config-schema/issues/140)) ([a58f507](https://github.com/rudderlabs/rudder-config-schema/commit/a58f507ab51ae812ac0a9751594c6c2ad40ddeec))
* **destination:** onboard discord ([#227](https://github.com/rudderlabs/rudder-config-schema/issues/227)) ([7407f26](https://github.com/rudderlabs/rudder-config-schema/commit/7407f264da59e1a45ad1a53eac83637bc9b0b68b))
* **destination:** onboard persistIq ([#164](https://github.com/rudderlabs/rudder-config-schema/issues/164)) ([0619326](https://github.com/rudderlabs/rudder-config-schema/commit/06193265ed48e91aed2996431e57c14071426902))
* **destination:** onboard pipedream ([#223](https://github.com/rudderlabs/rudder-config-schema/issues/223)) ([46e612c](https://github.com/rudderlabs/rudder-config-schema/commit/46e612c4ee5fe4d3f4ff34c7789f8ea840e9d462))
* **destination:** onboard pipedream as event stream source ([#208](https://github.com/rudderlabs/rudder-config-schema/issues/208)) ([c044f40](https://github.com/rudderlabs/rudder-config-schema/commit/c044f40de05484ee532f9ee76630988a97712724))
* **destination:** onboard satismeter destination and source ([#156](https://github.com/rudderlabs/rudder-config-schema/issues/156)) ([c90d9e7](https://github.com/rudderlabs/rudder-config-schema/commit/c90d9e7e803b05a68f92fff9b584301e79e253c9))
* **destinations:** support for dedup key in Braze ([#120](https://github.com/rudderlabs/rudder-config-schema/issues/120)) ([b4d058f](https://github.com/rudderlabs/rudder-config-schema/commit/b4d058f74412f68a119b39b2019712c2ce2b1b3c))
* **destination:** support custom mapping with client_id for ga4 destination ([#104](https://github.com/rudderlabs/rudder-config-schema/issues/104)) ([9cc40a0](https://github.com/rudderlabs/rudder-config-schema/commit/9cc40a0d42718cadd7ae37b976cc90068323d3f6))
* enable delete support for ga ([#102](https://github.com/rudderlabs/rudder-config-schema/issues/102)) ([a1842d2](https://github.com/rudderlabs/rudder-config-schema/commit/a1842d2a7ed6ffed6f4923e27a0276d01c349447))
* ga4 config schema changes ([#247](https://github.com/rudderlabs/rudder-config-schema/issues/247)) ([2a962e7](https://github.com/rudderlabs/rudder-config-schema/commit/2a962e792a47957d39b4f627427e384f8853dc43))
* ga4 hybrid mode support ([#119](https://github.com/rudderlabs/rudder-config-schema/issues/119)) ([4f5efaf](https://github.com/rudderlabs/rudder-config-schema/commit/4f5efaf5f9a0a9223f801c85a32e657f00c01177))
* ga4 hybrid mode support ([#196](https://github.com/rudderlabs/rudder-config-schema/issues/196)) ([7ca38f3](https://github.com/rudderlabs/rudder-config-schema/commit/7ca38f3de8f8d0d055557d4e2cac3429c8db2076))
* ga4 hybrid mode support ([#214](https://github.com/rudderlabs/rudder-config-schema/issues/214)) ([7ecbaa5](https://github.com/rudderlabs/rudder-config-schema/commit/7ecbaa57a7beb80ac98f0717ac87e78e3e780f7b))
* google analytics v4 release ([#202](https://github.com/rudderlabs/rudder-config-schema/issues/202)) ([0315e65](https://github.com/rudderlabs/rudder-config-schema/commit/0315e6507e569c4a5ffcc72f1e81bac5766adbcc))
* hide moengage source from prod ([#255](https://github.com/rudderlabs/rudder-config-schema/issues/255)) ([7387bca](https://github.com/rudderlabs/rudder-config-schema/commit/7387bca688d8e80101ddc7ce503eebfbce675b68))
* hotfix 1.0.9 ([#100](https://github.com/rudderlabs/rudder-config-schema/issues/100)) ([fc850e3](https://github.com/rudderlabs/rudder-config-schema/commit/fc850e39d67e135946260c73ec7bfc7eecb0f1ed)), closes [#89](https://github.com/rudderlabs/rudder-config-schema/issues/89)
* hotfix 1.1.1 ([#124](https://github.com/rudderlabs/rudder-config-schema/issues/124)) ([3273a16](https://github.com/rudderlabs/rudder-config-schema/commit/3273a16a125d4f2ed5b743e6eddfb4ce25daddde)), closes [#123](https://github.com/rudderlabs/rudder-config-schema/issues/123)
* impact radius - onbaord impact radius ([#225](https://github.com/rudderlabs/rudder-config-schema/issues/225)) ([72dfb30](https://github.com/rudderlabs/rudder-config-schema/commit/72dfb30e5ff90ab3cb51530e6cfed359806c1c7c))
* **integration:** Adobe Analytics - add schema validations ([#142](https://github.com/rudderlabs/rudder-config-schema/issues/142)) ([2a3b221](https://github.com/rudderlabs/rudder-config-schema/commit/2a3b22132c1e53c380f18356caf3f8128f47bfa8))
* **integration:** Adobe Analytics - fix schema validations ([#144](https://github.com/rudderlabs/rudder-config-schema/issues/144)) ([5f5135c](https://github.com/rudderlabs/rudder-config-schema/commit/5f5135cf6117636a71b7b8b32bab5a005d5b9d34))
* **integration:** adobe_analytics-remove supportedsourcevalidation ([#190](https://github.com/rudderlabs/rudder-config-schema/issues/190)) ([9cc2e42](https://github.com/rudderlabs/rudder-config-schema/commit/9cc2e42172b298e55d055c84e3ca0ebeba488243))
* **integration:** Iterable - useNativeSDK set to checkbox ([efac387](https://github.com/rudderlabs/rudder-config-schema/commit/efac3877ee4b6727a75125c584c13d92d7f644fa))
* **integration:** Marketo UI label updates ([#105](https://github.com/rudderlabs/rudder-config-schema/issues/105)) ([ae462f4](https://github.com/rudderlabs/rudder-config-schema/commit/ae462f484cc14805dcce7289d90a95ba51f9588e))
* **integrations:** update primary email for zendesk ([#151](https://github.com/rudderlabs/rudder-config-schema/issues/151)) ([d19913d](https://github.com/rudderlabs/rudder-config-schema/commit/d19913dff3530b8d106a83f18010bc92af705d96))
* **Integration:** support for track call ([#29](https://github.com/rudderlabs/rudder-config-schema/issues/29)) ([f703e6d](https://github.com/rudderlabs/rudder-config-schema/commit/f703e6dc66813bf86117cde8649e058f38dc47df))
* **mailjet:** onboarding mailjet destination ([#31](https://github.com/rudderlabs/rudder-config-schema/issues/31)) ([f718663](https://github.com/rudderlabs/rudder-config-schema/commit/f7186635062ea8e4be5bd60435e5298898788ccc))
* **new integration:** iterable-web-device-mode ([#28](https://github.com/rudderlabs/rudder-config-schema/issues/28)) ([8b4e57e](https://github.com/rudderlabs/rudder-config-schema/commit/8b4e57ee1e5fdac733e72c7a4ac7112b2e0fd7f2))
* **new integration:** onboard TikTok_Ads_Offline_Events destination ([#241](https://github.com/rudderlabs/rudder-config-schema/issues/241)) ([ef329cc](https://github.com/rudderlabs/rudder-config-schema/commit/ef329cc2195cd77552bc138b5f480757704c4782))
* **new integration:** onboarding qualaroo device mode destination ([#78](https://github.com/rudderlabs/rudder-config-schema/issues/78)) ([d7add66](https://github.com/rudderlabs/rudder-config-schema/commit/d7add6636ad8c878decc2549a73599d51bfb3bf1))
* **new integration:** onboarding sendinblue destination ([#181](https://github.com/rudderlabs/rudder-config-schema/issues/181)) ([474c722](https://github.com/rudderlabs/rudder-config-schema/commit/474c72200203eb897fb9b535244e2e50e0870711))
* onboard moengage source ([#224](https://github.com/rudderlabs/rudder-config-schema/issues/224)) ([a5f1944](https://github.com/rudderlabs/rudder-config-schema/commit/a5f194409a05a7ada90d5c5dd37596954ee71df8))
* onboard olark source ([#166](https://github.com/rudderlabs/rudder-config-schema/issues/166)) ([9f6c31d](https://github.com/rudderlabs/rudder-config-schema/commit/9f6c31d55c3ed3f4b20a700c109fd21317fca6ad))
* onboard olark web device mode ([#179](https://github.com/rudderlabs/rudder-config-schema/issues/179)) ([f134c88](https://github.com/rudderlabs/rudder-config-schema/commit/f134c88be25c505b16d9232eb73f99e19bfaca79))
* onboard pagerduty destination ([#231](https://github.com/rudderlabs/rudder-config-schema/issues/231)) ([af545d1](https://github.com/rudderlabs/rudder-config-schema/commit/af545d1eb181c5d17a981af1d1c91775bf9707c7))
* onboard pagerduty source ([#220](https://github.com/rudderlabs/rudder-config-schema/issues/220)) ([cfdacbd](https://github.com/rudderlabs/rudder-config-schema/commit/cfdacbd988ca64048fdabf6d9521c19cad7ead86))
* onboarding marketo static list destination ([#103](https://github.com/rudderlabs/rudder-config-schema/issues/103)) ([be6c0ab](https://github.com/rudderlabs/rudder-config-schema/commit/be6c0ab558fca8af6670f675b4ac0e7442c8de92))
* onboarding microsoft clarity ([#132](https://github.com/rudderlabs/rudder-config-schema/issues/132)) ([614f3a3](https://github.com/rudderlabs/rudder-config-schema/commit/614f3a33fefb4ce1f1fb93c1b7a118e583c330b9))
* onboarding multi topic support configs for kafka destination ([#115](https://github.com/rudderlabs/rudder-config-schema/issues/115)) ([2a32d02](https://github.com/rudderlabs/rudder-config-schema/commit/2a32d02b8e603c714edf845188ed8d800892e298))
* **Podsights:** onboarding new destination ([#63](https://github.com/rudderlabs/rudder-config-schema/issues/63)) ([1f13d94](https://github.com/rudderlabs/rudder-config-schema/commit/1f13d94e004d442f40547dd2104b6f54acc2792e))
* release v1.0.2 ([a3605a4](https://github.com/rudderlabs/rudder-config-schema/commit/a3605a4f377cbc6a6b32c06cf53fd60026e82cbf))
* release version1.0.3 ([8b71983](https://github.com/rudderlabs/rudder-config-schema/commit/8b71983bb9e91571e50b2bd92dec3f830d676474))
* release version1.0.4 ([c783ee6](https://github.com/rudderlabs/rudder-config-schema/commit/c783ee6f9978356b9b194c5d3fa6b727bb31bf1c))
* removed preRequisiteField for supportDedup property in Braze's ui_config.json ([#244](https://github.com/rudderlabs/rudder-config-schema/issues/244)) ([3a8f28a](https://github.com/rudderlabs/rudder-config-schema/commit/3a8f28aa118cd3466cbdebac9a8410eb142b2bcb))
* revert ga4 hybrid mode ([#261](https://github.com/rudderlabs/rudder-config-schema/issues/261)) ([e332c9b](https://github.com/rudderlabs/rudder-config-schema/commit/e332c9b791301fb9322e71a3bcd7d316449e8972))
* **s3-source:** added configuration for validation and cross account roles ([#162](https://github.com/rudderlabs/rudder-config-schema/issues/162)) ([0214723](https://github.com/rudderlabs/rudder-config-schema/commit/02147232546647b20ece0c5cf542222cbe3c9f80))
* sendgrid idetify and user deletion support ([#112](https://github.com/rudderlabs/rudder-config-schema/issues/112)) ([78d2f0d](https://github.com/rudderlabs/rudder-config-schema/commit/78d2f0d0cc1b84098341eb7938a3ae0566e67855))
* sendgrid idetify and user deletion support ([#127](https://github.com/rudderlabs/rudder-config-schema/issues/127)) ([ffb10c1](https://github.com/rudderlabs/rudder-config-schema/commit/ffb10c148bebe347822cc9948d0a26fe65ea6db4))
* subscription support in braze ([#175](https://github.com/rudderlabs/rudder-config-schema/issues/175)) ([b744a3c](https://github.com/rudderlabs/rudder-config-schema/commit/b744a3ce71d446195ebbd72f53ba3ba4d34248b2))
* support nested array ops braze ([#215](https://github.com/rudderlabs/rudder-config-schema/issues/215)) ([b7d592d](https://github.com/rudderlabs/rudder-config-schema/commit/b7d592d5f34455cdc22b957b45eaf53e98d0fb0f))
* update config for bing ads source release ([#217](https://github.com/rudderlabs/rudder-config-schema/issues/217)) ([d0884fa](https://github.com/rudderlabs/rudder-config-schema/commit/d0884fad309fdaf43a62dc7df06e3abaf7f9a4b5))
* update footernote in bigquery ([#189](https://github.com/rudderlabs/rudder-config-schema/issues/189)) ([b0af34c](https://github.com/rudderlabs/rudder-config-schema/commit/b0af34cbfa71ae0cac30406d9e6100e391ec0bd1))


### Bug Fixes

* add coming soon and remove from audience ([#139](https://github.com/rudderlabs/rudder-config-schema/issues/139)) ([d9d9a26](https://github.com/rudderlabs/rudder-config-schema/commit/d9d9a2632dd858bd1507c452613ce0d14a400842))
* add coming soon and remove from audience ([#143](https://github.com/rudderlabs/rudder-config-schema/issues/143)) ([638a957](https://github.com/rudderlabs/rudder-config-schema/commit/638a957f1d73f4a6862c3544857dd59914973663))
* add TestCase and update config for Podsights ([#92](https://github.com/rudderlabs/rudder-config-schema/issues/92)) ([4375261](https://github.com/rudderlabs/rudder-config-schema/commit/43752611be9ed2080085cffeb70e81eb91e71ab7))
* added onetrustCookieCategories in destinations schema ([#163](https://github.com/rudderlabs/rudder-config-schema/issues/163)) ([29daf01](https://github.com/rudderlabs/rudder-config-schema/commit/29daf014be7d8a7a04cce5b3858b10500a23ca63))
* braze update supportDedup key and footernote ([#176](https://github.com/rudderlabs/rudder-config-schema/issues/176)) ([95421be](https://github.com/rudderlabs/rudder-config-schema/commit/95421bef953df2f9262fb4e0380ec22656d3c757))
* content_type is customised for facebook offline conversions ([#57](https://github.com/rudderlabs/rudder-config-schema/issues/57)) ([b37c7e2](https://github.com/rudderlabs/rudder-config-schema/commit/b37c7e2c1e88f6d16b8a2dbd7b469e3dc910b44a))
* facebook_offline_conversions access token length issue ([#133](https://github.com/rudderlabs/rudder-config-schema/issues/133)) ([b9cc76e](https://github.com/rudderlabs/rudder-config-schema/commit/b9cc76ee522aa2bd02e6fd077c24c7873a68fed8))
* fix impact radius regex ([#258](https://github.com/rudderlabs/rudder-config-schema/issues/258)) ([8981b1b](https://github.com/rudderlabs/rudder-config-schema/commit/8981b1bf498a7cacf3c8255b361c6b6bc7f18320))
* fixed schema validation ([41536f4](https://github.com/rudderlabs/rudder-config-schema/commit/41536f4f08659474ec1eb128b8b47f534de9bfd0))
* footer note update on Podsights ([#98](https://github.com/rudderlabs/rudder-config-schema/issues/98)) ([cf4404e](https://github.com/rudderlabs/rudder-config-schema/commit/cf4404eb5498808bafa67473a2a24d8212b1c1b3))
* Footernode updated for Engage ([15526b7](https://github.com/rudderlabs/rudder-config-schema/commit/15526b79231bcaa7932559b699ab1fc33c1523a8))
* freshdesk spec file cleanup ([3bf07c3](https://github.com/rudderlabs/rudder-config-schema/commit/3bf07c3581ff5a4d0919cf1c0d5783e782c543f1))
* google-ads source config ([#169](https://github.com/rudderlabs/rudder-config-schema/issues/169)) ([a3c559c](https://github.com/rudderlabs/rudder-config-schema/commit/a3c559c16528e4feecb6a5ff4f614a2996a433f3))
* hubspot token hotfix ([e8f2b4c](https://github.com/rudderlabs/rudder-config-schema/commit/e8f2b4cee7be581a8ba53c85eebebb9fe8827a95))
* **integration:** adobe analytics - update regex for video events mapping to allow specific values ([#171](https://github.com/rudderlabs/rudder-config-schema/issues/171)) ([3133a4e](https://github.com/rudderlabs/rudder-config-schema/commit/3133a4e8dfc9687d80212aed6c0cd84ce1fe7fd9))
* marketo static list: removing preview tag ([#188](https://github.com/rudderlabs/rudder-config-schema/issues/188)) ([25983ef](https://github.com/rudderlabs/rudder-config-schema/commit/25983efbfa8f95f6ef3963963f6098f7e6f197ff))
* move files to new directory structure ([#257](https://github.com/rudderlabs/rudder-config-schema/issues/257)) ([e3a7ade](https://github.com/rudderlabs/rudder-config-schema/commit/e3a7aded5ea60af10c66ec3048a0890e94282c37))
* **qualaroo:** remove eventsList schema ([#87](https://github.com/rudderlabs/rudder-config-schema/issues/87)) ([9511a13](https://github.com/rudderlabs/rudder-config-schema/commit/9511a132d1e43f7a712fb5f75d411387ebca9cf5))
* remove iam role support ([e725fee](https://github.com/rudderlabs/rudder-config-schema/commit/e725fee95de7597e4b4075560af7bb9734e8fc1c))
* remove iam role support ([5032df2](https://github.com/rudderlabs/rudder-config-schema/commit/5032df2a2ea954902c934b0dbf0c8e1c24a3232a))
* removes oauth role from singer gsc ([#67](https://github.com/rudderlabs/rudder-config-schema/issues/67)) ([d73e610](https://github.com/rudderlabs/rudder-config-schema/commit/d73e6100881820733848210b79fe01a18e2e1b07))
* removes oauthrole for google sheets ([#117](https://github.com/rudderlabs/rudder-config-schema/issues/117)) ([1a56973](https://github.com/rudderlabs/rudder-config-schema/commit/1a5697392933d317e8e78b8bd4b69e300f6b9ba3))
* removing preview tag ([#167](https://github.com/rudderlabs/rudder-config-schema/issues/167)) ([ffb79ba](https://github.com/rudderlabs/rudder-config-schema/commit/ffb79ba1af2e495a421cdbaff6d316ce58a63722))
* rename files to the latest format ([efecaf7](https://github.com/rudderlabs/rudder-config-schema/commit/efecaf7652d828beaa90c6360362a43fd6a4bf30))
* resolve conflicts with master ([#107](https://github.com/rudderlabs/rudder-config-schema/issues/107)) ([fef97a8](https://github.com/rudderlabs/rudder-config-schema/commit/fef97a8560f6aaf1cc6daa3c9147d1d1ede5ddbd)), closes [#80](https://github.com/rudderlabs/rudder-config-schema/issues/80) [#100](https://github.com/rudderlabs/rudder-config-schema/issues/100) [#89](https://github.com/rudderlabs/rudder-config-schema/issues/89)
* revert bq changes ([#270](https://github.com/rudderlabs/rudder-config-schema/issues/270)) ([7775865](https://github.com/rudderlabs/rudder-config-schema/commit/77758655d8ac27d090a36fb2f316e3814bff5ac7))
* revert personalize config changed to remove iam role ([#122](https://github.com/rudderlabs/rudder-config-schema/issues/122)) ([6f66035](https://github.com/rudderlabs/rudder-config-schema/commit/6f6603582947d62253e2ffbc74719222ddbd8216))
* **satismeter:** set hidden to false ([#207](https://github.com/rudderlabs/rudder-config-schema/issues/207)) ([c4f6723](https://github.com/rudderlabs/rudder-config-schema/commit/c4f6723ed1e3e44663fe7c7a8e119a65d7f0f6b4))
* sendinblue regex ([#269](https://github.com/rudderlabs/rudder-config-schema/issues/269)) ([424ff9c](https://github.com/rudderlabs/rudder-config-schema/commit/424ff9c52e4342a14b94a236c66a3aee97cbc83f))
* **sendinblue:** schema ([#262](https://github.com/rudderlabs/rudder-config-schema/issues/262)) ([00bec4a](https://github.com/rudderlabs/rudder-config-schema/commit/00bec4a72bf15d90658a9d3ba41a745a2ca4cab0))
* **sendinblue:** schema ([#263](https://github.com/rudderlabs/rudder-config-schema/issues/263)) ([5888a95](https://github.com/rudderlabs/rudder-config-schema/commit/5888a95d570a50556e82e15894d4fac1dd1bf744))
* set preview to true (satismeter, axeptio, microsoft_clarity) ([#206](https://github.com/rudderlabs/rudder-config-schema/issues/206)) ([625d76f](https://github.com/rudderlabs/rudder-config-schema/commit/625d76fbd8508a387f5959e2af578a306481363a))
* singer salesforce new version ([#89](https://github.com/rudderlabs/rudder-config-schema/issues/89)) ([761ba3d](https://github.com/rudderlabs/rudder-config-schema/commit/761ba3dfa4207521ce6abca34c3820787784925c))
* supportedSourcesValidation in dbconfig ([#174](https://github.com/rudderlabs/rudder-config-schema/issues/174)) ([2112936](https://github.com/rudderlabs/rudder-config-schema/commit/2112936894e65b8c723b24641e1b4e7bb9291857))
* typo introduced while hiding facebook ads ([#238](https://github.com/rudderlabs/rudder-config-schema/issues/238)) ([1c5d860](https://github.com/rudderlabs/rudder-config-schema/commit/1c5d860d9fecb72a8ebd74ad68eb556f49db91ab))
* typo introduced while hiding facebook ads ([#238](https://github.com/rudderlabs/rudder-config-schema/issues/238)) ([2b63885](https://github.com/rudderlabs/rudder-config-schema/commit/2b63885619aace90910ac6c748c2e62cce236837))
* update google sheets image ([#194](https://github.com/rudderlabs/rudder-config-schema/issues/194)) ([3057183](https://github.com/rudderlabs/rudder-config-schema/commit/30571838340d13e64c5d7a28073321150f5a3a17))
* update singer_hubspot image ([68000da](https://github.com/rudderlabs/rudder-config-schema/commit/68000da2fed52f065ab938b75f308575cc51dbf9))
* updated factorsAI configs ([c586f5b](https://github.com/rudderlabs/rudder-config-schema/commit/c586f5b99db1738f746ada41d193589f09e7ecf6))
* updated flutter device mode support for destinations ADJ, AM, AppCenter, Braze, Firebase, Leanplum ([65bd102](https://github.com/rudderlabs/rudder-config-schema/commit/65bd102752a9a9bb93b0f8592125168c23ef0ec9))
* Webhook category added ([#81](https://github.com/rudderlabs/rudder-config-schema/issues/81)) ([0239729](https://github.com/rudderlabs/rudder-config-schema/commit/023972953dee246a6b60ecc2c3220bf8b94c45c1))

### [1.6.5](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.4...1.6.5) (2023-02-13)

### [1.6.4](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.3...1.6.4) (2023-02-10)

### [1.6.3](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.2...1.6.3) (2023-02-07)


### Bug Fixes

* googleads dynamicRemarketing flag changes ([#367](https://github.com/rudderlabs/rudder-config-schema/issues/367)) ([e214d1e](https://github.com/rudderlabs/rudder-config-schema/commit/e214d1ecde7de648a4f244890133dedd7e747e06))

### [1.6.2](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.1...1.6.2) (2023-02-07)


### Bug Fixes

* update googleAds config  ([#364](https://github.com/rudderlabs/rudder-config-schema/issues/364)) ([e2abc96](https://github.com/rudderlabs/rudder-config-schema/commit/e2abc9609bd884bf6934cf12f6eade9c204cfe73))

### [1.6.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.0...1.6.1) (2023-02-03)

## [1.6.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.5.0...1.6.0) (2023-02-02)


### Features

* add time window layout to s3 datalake glue ([#348](https://github.com/rudderlabs/rudder-config-schema/issues/348)) ([784bd3f](https://github.com/rudderlabs/rudder-config-schema/commit/784bd3fca1f50899430c544608cee4234cf858e9))
* added catalog for databricks ([#253](https://github.com/rudderlabs/rudder-config-schema/issues/253)) ([#338](https://github.com/rudderlabs/rudder-config-schema/issues/338)) ([56e9bf8](https://github.com/rudderlabs/rudder-config-schema/commit/56e9bf8c5fa76200c0611833673b648d0109fc5c))
* added OneTrust consent support for mobile device modes ([19454ee](https://github.com/rudderlabs/rudder-config-schema/commit/19454ee8b72a8e0d6f7348fbc02ae860323623a4))
* added use rudder storage option to deltalake ([#349](https://github.com/rudderlabs/rudder-config-schema/issues/349)) ([3ad3317](https://github.com/rudderlabs/rudder-config-schema/commit/3ad3317b17e0a5f2b8074c35c3863507d1a6cdd4))
* **CDK v2:** enabling CDK v2 comparison for webhook ([#341](https://github.com/rudderlabs/rudder-config-schema/issues/341)) ([33e59c5](https://github.com/rudderlabs/rudder-config-schema/commit/33e59c5c43334f567689de70e971081df093f661))
* **destination:** onboard criteo audience integration ([#320](https://github.com/rudderlabs/rudder-config-schema/issues/320)) ([fd6fbb6](https://github.com/rudderlabs/rudder-config-schema/commit/fd6fbb61ead9b7a576a9f32326336a302f35a0da))
* **integration:** rockerbox- add support for custom properties ([#315](https://github.com/rudderlabs/rudder-config-schema/issues/315)) ([a06c9d5](https://github.com/rudderlabs/rudder-config-schema/commit/a06c9d539b9aebef04e85f05515366707c54762a))
* **integration:** rockerbox- revert adding support for custom properties ([#345](https://github.com/rudderlabs/rudder-config-schema/issues/345)) ([2de567a](https://github.com/rudderlabs/rudder-config-schema/commit/2de567a37943f1d95621f35b6d58a93f49b99f75))
* **mailchimp:** add support for track call ([#327](https://github.com/rudderlabs/rudder-config-schema/issues/327)) ([16ce89a](https://github.com/rudderlabs/rudder-config-schema/commit/16ce89afa5a6faa76f3877365b524cf46ae1d3e9))
* **optimizely:** add fullstack cloude mode support ([#317](https://github.com/rudderlabs/rudder-config-schema/issues/317)) ([cda7dd5](https://github.com/rudderlabs/rudder-config-schema/commit/cda7dd594cdc4dafc0f3e77b43faa18686347fd0))


### Bug Fixes

* add supportedMessageTypes in GAEC ([#339](https://github.com/rudderlabs/rudder-config-schema/issues/339)) ([8a93e92](https://github.com/rudderlabs/rudder-config-schema/commit/8a93e92276e70268f5e49c0de94cc9553b24ee56))
* add tag option to standard-version command ([fc8264b](https://github.com/rudderlabs/rudder-config-schema/commit/fc8264b543005a6a6ed6e4077d8125a7b9f60480))
* adobe_analytics schema regex ([#325](https://github.com/rudderlabs/rudder-config-schema/issues/325)) ([9751dba](https://github.com/rudderlabs/rudder-config-schema/commit/9751dba7c141e8507edcb452a4da03d13b4b6351))
* **changelog:** fixing changelog for release 1.4.0, 1.3.7 and 1.3.4 ([#333](https://github.com/rudderlabs/rudder-config-schema/issues/333)) ([b2d5604](https://github.com/rudderlabs/rudder-config-schema/commit/b2d5604abe825c81acab638464b9de224c08a3fb))
* default blockPageViewEvent enabled to prevent duplicate page calls ([#340](https://github.com/rudderlabs/rudder-config-schema/issues/340)) ([24f8fcf](https://github.com/rudderlabs/rudder-config-schema/commit/24f8fcfec22cf06849bfed76f08584024c109489))
* optimizely fullstack schema ([#344](https://github.com/rudderlabs/rudder-config-schema/issues/344)) ([e42af44](https://github.com/rudderlabs/rudder-config-schema/commit/e42af44f05ed72c51c590839b635b18e7808e2df))

### [1.4.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.4.0...1.4.1) (2023-01-24)


### Bug Fixes

* move mp,zendesk,sfmc to processor ([7433e22](https://github.com/rudderlabs/rudder-config-schema/commit/7433e229c1426a7cd5d0aefc2fd94442170b9e45))

## [1.4.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.7...1.4.0) (2023-01-24)


### Features

* **destination:** onboard lemnisk integration ([#306](https://github.com/rudderlabs/rudder-config-schema/issues/306)) ([392a9d1](https://github.com/rudderlabs/rudder-config-schema/commit/392a9d1ae1be9f4046c4eeea0f49b1b9166a5fcd))
* ga4 hybrid mode support ([#316](https://github.com/rudderlabs/rudder-config-schema/issues/316)) ([724e865](https://github.com/rudderlabs/rudder-config-schema/commit/724e86516a8b5d86aefeb3db6da0e54ac1ebc569))
* updated the ui-config of amplitude to version2 ([#318](https://github.com/rudderlabs/rudder-config-schema/issues/318)) ([caa8bf8](https://github.com/rudderlabs/rudder-config-schema/commit/caa8bf8108fe213c6162eb800a2b17e549330925))


### Bug Fixes

* disables skills resource in freshdesk ([f2c7343](https://github.com/rudderlabs/rudder-config-schema/commit/f2c7343bb7c411685c92609d67bffdfd59bc3b64))

### [1.3.7](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.6...1.3.7) (2023-01-18)


### Features

* add axeptio into prod ([#302](https://github.com/rudderlabs/rudder-config-schema/issues/302)) ([231db08](https://github.com/rudderlabs/rudder-config-schema/commit/231db0873b9bd948521d69fa7cc25efdd621a394))
* add microsoft clarity to prod ([#275](https://github.com/rudderlabs/rudder-config-schema/issues/275)) ([9327566](https://github.com/rudderlabs/rudder-config-schema/commit/9327566284652fb48c98da3ca31776661df03e66))
* added catalog for databricks ([#253](https://github.com/rudderlabs/rudder-config-schema/issues/253)) ([#308](https://github.com/rudderlabs/rudder-config-schema/issues/308)) ([4446798](https://github.com/rudderlabs/rudder-config-schema/commit/4446798083cff92760b5dac7ee6b7d2a9939e0c9))
* update footernote in bigquerystream ([#271](https://github.com/rudderlabs/rudder-config-schema/issues/271)) ([4aeaa42](https://github.com/rudderlabs/rudder-config-schema/commit/4aeaa42240d237e784bb8ea397ad69a003573dc4))


### Bug Fixes

* bing ads updated image ([#292](https://github.com/rudderlabs/rudder-config-schema/issues/292)) ([e3891c1](https://github.com/rudderlabs/rudder-config-schema/commit/e3891c1a8ca2567a95e398d1dfbceefa6013edc5))

### [1.3.6](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.5...1.3.6) (2023-01-13)


### Bug Fixes

* reenable ga4 page call support for cloud mode ([#299](https://github.com/rudderlabs/rudder-config-schema/issues/299)) ([8bf3643](https://github.com/rudderlabs/rudder-config-schema/commit/8bf3643c4edd268a562f67f79f4a0b3ea22248d1))

### [1.3.5](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.4...1.3.5) (2023-01-13)


### Bug Fixes

* enanble pro and enterpise for cdkv2 comparison test ([#293](https://github.com/rudderlabs/rudder-config-schema/issues/293)) ([a6593dc](https://github.com/rudderlabs/rudder-config-schema/commit/a6593dcac8f96d2ad925121095ce307a3daabe5a))

### [1.3.4](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.3...1.3.4) (2023-01-13)

### [1.3.3](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.2...1.3.3) (2023-01-13)


### Bug Fixes

* enable cdkv2 for algolia and pinterest ([630644e](https://github.com/rudderlabs/rudder-config-schema/commit/630644e5466d5d624e76f52dd37d1524e71ef499))
* revert a specific commit from [#253](https://github.com/rudderlabs/rudder-config-schema/issues/253) ([#284](https://github.com/rudderlabs/rudder-config-schema/issues/284)) ([856c9b9](https://github.com/rudderlabs/rudder-config-schema/commit/856c9b91c3f33bef5ca8c46b1d0b751629574b8f))

### [1.3.2](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.1...1.3.2) (2023-01-12)


### Bug Fixes

* hotfix intercom image update ([#280](https://github.com/rudderlabs/rudder-config-schema/issues/280)) ([0aeef10](https://github.com/rudderlabs/rudder-config-schema/commit/0aeef10eed47b0715fd878c2753c0c298ab794b3))

### [1.3.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.3.0...1.3.1) (2023-01-12)


### Bug Fixes

* destination transformation change from processor to router ([#246](https://github.com/rudderlabs/rudder-config-schema/issues/246)) ([2c3b461](https://github.com/rudderlabs/rudder-config-schema/commit/2c3b46186db5e5d286c293a1af644a98f82d2123))

## [1.3.0](https://github.com/rudderlabs/rudder-config-schema/compare/a615d2b76ce7cf7cebb5c1241806b5de3de2f857...1.3.0) (2023-01-12)


### Features

* add config for enabling iam role for streaming destinations ([#121](https://github.com/rudderlabs/rudder-config-schema/issues/121)) ([0ec3a1e](https://github.com/rudderlabs/rudder-config-schema/commit/0ec3a1e79a9c8ed49f45f3f2f60d5783691cf086))
* add validations and made it a node repo ([a615d2b](https://github.com/rudderlabs/rudder-config-schema/commit/a615d2b76ce7cf7cebb5c1241806b5de3de2f857))
* added block pageview toggle ([#264](https://github.com/rudderlabs/rudder-config-schema/issues/264)) ([2f4f48c](https://github.com/rudderlabs/rudder-config-schema/commit/2f4f48c64c6135e1a4abdc693ab78d6cbb12b7c4))
* added Braze dedup support for mobile SDKs ([#242](https://github.com/rudderlabs/rudder-config-schema/issues/242)) ([1912792](https://github.com/rudderlabs/rudder-config-schema/commit/1912792a39dd869ee329d38c0cc938b95d508971))
* added IAM role based configurations for warehouse destinations ([#198](https://github.com/rudderlabs/rudder-config-schema/issues/198)) ([19220d2](https://github.com/rudderlabs/rudder-config-schema/commit/19220d251434821f29712a89f1f7b5800e09f06f))
* added profileId in dest config campaign manager ([#130](https://github.com/rudderlabs/rudder-config-schema/issues/130)) ([f9e641e](https://github.com/rudderlabs/rudder-config-schema/commit/f9e641e7597c3138ab72f39a088ca1f5aee03007))
* added singer-freshdesk ([8958966](https://github.com/rudderlabs/rudder-config-schema/commit/89589660fdd3824f655133442e4a9978929d1dc6))
* added singer-freshdesk ([a2fbad6](https://github.com/rudderlabs/rudder-config-schema/commit/a2fbad63a7ab5ba7760eb18738bbc08985133c6b))
* **algolia:** configure cdk v2 threshold ([#70](https://github.com/rudderlabs/rudder-config-schema/issues/70)) ([b964439](https://github.com/rudderlabs/rudder-config-schema/commit/b964439db84bbd6008245ecd15518df030df0e3c))
* allow usage of OneTrust category ids or names ([#237](https://github.com/rudderlabs/rudder-config-schema/issues/237)) ([4892d4e](https://github.com/rudderlabs/rudder-config-schema/commit/4892d4eee308b8fdb8bad8bb062b01f37b1ad8b9))
* **braze:** braze logs feat ([#251](https://github.com/rudderlabs/rudder-config-schema/issues/251)) ([5758d23](https://github.com/rudderlabs/rudder-config-schema/commit/5758d2343fd2abe0eb1c63fdfe633c495ff5b51d))
* **braze:** braze logs feat ([#254](https://github.com/rudderlabs/rudder-config-schema/issues/254)) ([7e8cc34](https://github.com/rudderlabs/rudder-config-schema/commit/7e8cc349640e835d05e9eb383fd4e95c13e1d7e0))
* **braze:** braze logs flag ([#252](https://github.com/rudderlabs/rudder-config-schema/issues/252)) ([c2f8017](https://github.com/rudderlabs/rudder-config-schema/commit/c2f80170113a9f91d9789903fdee7ed7335068b5))
* **braze:** make logs visibility configurable braze ([#240](https://github.com/rudderlabs/rudder-config-schema/issues/240)) ([c052a6d](https://github.com/rudderlabs/rudder-config-schema/commit/c052a6d885eb8f773596900fcbf43b61c270271b))
* **dcm floodlight:** add iframe support ([#61](https://github.com/rudderlabs/rudder-config-schema/issues/61)) ([e1804c0](https://github.com/rudderlabs/rudder-config-schema/commit/e1804c0dcc28fbf1a6db4a37cb8e17a627bb37fa))
* **dcm floodlight:** add iframe support ([#80](https://github.com/rudderlabs/rudder-config-schema/issues/80)) ([559fbaa](https://github.com/rudderlabs/rudder-config-schema/commit/559fbaaa273c080bf227bbb1333cdaa524255b53))
* deploying singer freshdesk ([7aac54c](https://github.com/rudderlabs/rudder-config-schema/commit/7aac54caf4f5def3f9be4e477cffaf0359070407))
* **destination:** onboard awin integration ([#140](https://github.com/rudderlabs/rudder-config-schema/issues/140)) ([a58f507](https://github.com/rudderlabs/rudder-config-schema/commit/a58f507ab51ae812ac0a9751594c6c2ad40ddeec))
* **destination:** onboard discord ([#227](https://github.com/rudderlabs/rudder-config-schema/issues/227)) ([7407f26](https://github.com/rudderlabs/rudder-config-schema/commit/7407f264da59e1a45ad1a53eac83637bc9b0b68b))
* **destination:** onboard persistIq ([#164](https://github.com/rudderlabs/rudder-config-schema/issues/164)) ([0619326](https://github.com/rudderlabs/rudder-config-schema/commit/06193265ed48e91aed2996431e57c14071426902))
* **destination:** onboard pipedream ([#223](https://github.com/rudderlabs/rudder-config-schema/issues/223)) ([46e612c](https://github.com/rudderlabs/rudder-config-schema/commit/46e612c4ee5fe4d3f4ff34c7789f8ea840e9d462))
* **destination:** onboard pipedream as event stream source ([#208](https://github.com/rudderlabs/rudder-config-schema/issues/208)) ([c044f40](https://github.com/rudderlabs/rudder-config-schema/commit/c044f40de05484ee532f9ee76630988a97712724))
* **destination:** onboard satismeter destination and source ([#156](https://github.com/rudderlabs/rudder-config-schema/issues/156)) ([c90d9e7](https://github.com/rudderlabs/rudder-config-schema/commit/c90d9e7e803b05a68f92fff9b584301e79e253c9))
* **destinations:** support for dedup key in Braze ([#120](https://github.com/rudderlabs/rudder-config-schema/issues/120)) ([b4d058f](https://github.com/rudderlabs/rudder-config-schema/commit/b4d058f74412f68a119b39b2019712c2ce2b1b3c))
* **destination:** support custom mapping with client_id for ga4 destination ([#104](https://github.com/rudderlabs/rudder-config-schema/issues/104)) ([9cc40a0](https://github.com/rudderlabs/rudder-config-schema/commit/9cc40a0d42718cadd7ae37b976cc90068323d3f6))
* enable delete support for ga ([#102](https://github.com/rudderlabs/rudder-config-schema/issues/102)) ([a1842d2](https://github.com/rudderlabs/rudder-config-schema/commit/a1842d2a7ed6ffed6f4923e27a0276d01c349447))
* ga4 config schema changes ([#247](https://github.com/rudderlabs/rudder-config-schema/issues/247)) ([2a962e7](https://github.com/rudderlabs/rudder-config-schema/commit/2a962e792a47957d39b4f627427e384f8853dc43))
* ga4 hybrid mode support ([#119](https://github.com/rudderlabs/rudder-config-schema/issues/119)) ([4f5efaf](https://github.com/rudderlabs/rudder-config-schema/commit/4f5efaf5f9a0a9223f801c85a32e657f00c01177))
* ga4 hybrid mode support ([#196](https://github.com/rudderlabs/rudder-config-schema/issues/196)) ([7ca38f3](https://github.com/rudderlabs/rudder-config-schema/commit/7ca38f3de8f8d0d055557d4e2cac3429c8db2076))
* ga4 hybrid mode support ([#214](https://github.com/rudderlabs/rudder-config-schema/issues/214)) ([7ecbaa5](https://github.com/rudderlabs/rudder-config-schema/commit/7ecbaa57a7beb80ac98f0717ac87e78e3e780f7b))
* google analytics v4 release ([#202](https://github.com/rudderlabs/rudder-config-schema/issues/202)) ([0315e65](https://github.com/rudderlabs/rudder-config-schema/commit/0315e6507e569c4a5ffcc72f1e81bac5766adbcc))
* hide moengage source from prod ([#255](https://github.com/rudderlabs/rudder-config-schema/issues/255)) ([7387bca](https://github.com/rudderlabs/rudder-config-schema/commit/7387bca688d8e80101ddc7ce503eebfbce675b68))
* hotfix 1.0.9 ([#100](https://github.com/rudderlabs/rudder-config-schema/issues/100)) ([fc850e3](https://github.com/rudderlabs/rudder-config-schema/commit/fc850e39d67e135946260c73ec7bfc7eecb0f1ed)), closes [#89](https://github.com/rudderlabs/rudder-config-schema/issues/89)
* hotfix 1.1.1 ([#124](https://github.com/rudderlabs/rudder-config-schema/issues/124)) ([3273a16](https://github.com/rudderlabs/rudder-config-schema/commit/3273a16a125d4f2ed5b743e6eddfb4ce25daddde)), closes [#123](https://github.com/rudderlabs/rudder-config-schema/issues/123)
* impact radius - onbaord impact radius ([#225](https://github.com/rudderlabs/rudder-config-schema/issues/225)) ([72dfb30](https://github.com/rudderlabs/rudder-config-schema/commit/72dfb30e5ff90ab3cb51530e6cfed359806c1c7c))
* **integration:** Adobe Analytics - add schema validations ([#142](https://github.com/rudderlabs/rudder-config-schema/issues/142)) ([2a3b221](https://github.com/rudderlabs/rudder-config-schema/commit/2a3b22132c1e53c380f18356caf3f8128f47bfa8))
* **integration:** Adobe Analytics - fix schema validations ([#144](https://github.com/rudderlabs/rudder-config-schema/issues/144)) ([5f5135c](https://github.com/rudderlabs/rudder-config-schema/commit/5f5135cf6117636a71b7b8b32bab5a005d5b9d34))
* **integration:** adobe_analytics-remove supportedsourcevalidation ([#190](https://github.com/rudderlabs/rudder-config-schema/issues/190)) ([9cc2e42](https://github.com/rudderlabs/rudder-config-schema/commit/9cc2e42172b298e55d055c84e3ca0ebeba488243))
* **integration:** Iterable - useNativeSDK set to checkbox ([efac387](https://github.com/rudderlabs/rudder-config-schema/commit/efac3877ee4b6727a75125c584c13d92d7f644fa))
* **integration:** Marketo UI label updates ([#105](https://github.com/rudderlabs/rudder-config-schema/issues/105)) ([ae462f4](https://github.com/rudderlabs/rudder-config-schema/commit/ae462f484cc14805dcce7289d90a95ba51f9588e))
* **integrations:** update primary email for zendesk ([#151](https://github.com/rudderlabs/rudder-config-schema/issues/151)) ([d19913d](https://github.com/rudderlabs/rudder-config-schema/commit/d19913dff3530b8d106a83f18010bc92af705d96))
* **Integration:** support for track call ([#29](https://github.com/rudderlabs/rudder-config-schema/issues/29)) ([f703e6d](https://github.com/rudderlabs/rudder-config-schema/commit/f703e6dc66813bf86117cde8649e058f38dc47df))
* **mailjet:** onboarding mailjet destination ([#31](https://github.com/rudderlabs/rudder-config-schema/issues/31)) ([f718663](https://github.com/rudderlabs/rudder-config-schema/commit/f7186635062ea8e4be5bd60435e5298898788ccc))
* **new integration:** iterable-web-device-mode ([#28](https://github.com/rudderlabs/rudder-config-schema/issues/28)) ([8b4e57e](https://github.com/rudderlabs/rudder-config-schema/commit/8b4e57ee1e5fdac733e72c7a4ac7112b2e0fd7f2))
* **new integration:** onboard TikTok_Ads_Offline_Events destination ([#241](https://github.com/rudderlabs/rudder-config-schema/issues/241)) ([ef329cc](https://github.com/rudderlabs/rudder-config-schema/commit/ef329cc2195cd77552bc138b5f480757704c4782))
* **new integration:** onboarding qualaroo device mode destination ([#78](https://github.com/rudderlabs/rudder-config-schema/issues/78)) ([d7add66](https://github.com/rudderlabs/rudder-config-schema/commit/d7add6636ad8c878decc2549a73599d51bfb3bf1))
* **new integration:** onboarding sendinblue destination ([#181](https://github.com/rudderlabs/rudder-config-schema/issues/181)) ([474c722](https://github.com/rudderlabs/rudder-config-schema/commit/474c72200203eb897fb9b535244e2e50e0870711))
* onboard moengage source ([#224](https://github.com/rudderlabs/rudder-config-schema/issues/224)) ([a5f1944](https://github.com/rudderlabs/rudder-config-schema/commit/a5f194409a05a7ada90d5c5dd37596954ee71df8))
* onboard olark source ([#166](https://github.com/rudderlabs/rudder-config-schema/issues/166)) ([9f6c31d](https://github.com/rudderlabs/rudder-config-schema/commit/9f6c31d55c3ed3f4b20a700c109fd21317fca6ad))
* onboard olark web device mode ([#179](https://github.com/rudderlabs/rudder-config-schema/issues/179)) ([f134c88](https://github.com/rudderlabs/rudder-config-schema/commit/f134c88be25c505b16d9232eb73f99e19bfaca79))
* onboard pagerduty destination ([#231](https://github.com/rudderlabs/rudder-config-schema/issues/231)) ([af545d1](https://github.com/rudderlabs/rudder-config-schema/commit/af545d1eb181c5d17a981af1d1c91775bf9707c7))
* onboard pagerduty source ([#220](https://github.com/rudderlabs/rudder-config-schema/issues/220)) ([cfdacbd](https://github.com/rudderlabs/rudder-config-schema/commit/cfdacbd988ca64048fdabf6d9521c19cad7ead86))
* onboarding marketo static list destination ([#103](https://github.com/rudderlabs/rudder-config-schema/issues/103)) ([be6c0ab](https://github.com/rudderlabs/rudder-config-schema/commit/be6c0ab558fca8af6670f675b4ac0e7442c8de92))
* onboarding microsoft clarity ([#132](https://github.com/rudderlabs/rudder-config-schema/issues/132)) ([614f3a3](https://github.com/rudderlabs/rudder-config-schema/commit/614f3a33fefb4ce1f1fb93c1b7a118e583c330b9))
* onboarding multi topic support configs for kafka destination ([#115](https://github.com/rudderlabs/rudder-config-schema/issues/115)) ([2a32d02](https://github.com/rudderlabs/rudder-config-schema/commit/2a32d02b8e603c714edf845188ed8d800892e298))
* **Podsights:** onboarding new destination ([#63](https://github.com/rudderlabs/rudder-config-schema/issues/63)) ([1f13d94](https://github.com/rudderlabs/rudder-config-schema/commit/1f13d94e004d442f40547dd2104b6f54acc2792e))
* release v1.0.2 ([a3605a4](https://github.com/rudderlabs/rudder-config-schema/commit/a3605a4f377cbc6a6b32c06cf53fd60026e82cbf))
* release version1.0.3 ([8b71983](https://github.com/rudderlabs/rudder-config-schema/commit/8b71983bb9e91571e50b2bd92dec3f830d676474))
* release version1.0.4 ([c783ee6](https://github.com/rudderlabs/rudder-config-schema/commit/c783ee6f9978356b9b194c5d3fa6b727bb31bf1c))
* removed preRequisiteField for supportDedup property in Braze's ui_config.json ([#244](https://github.com/rudderlabs/rudder-config-schema/issues/244)) ([3a8f28a](https://github.com/rudderlabs/rudder-config-schema/commit/3a8f28aa118cd3466cbdebac9a8410eb142b2bcb))
* revert ga4 hybrid mode ([#261](https://github.com/rudderlabs/rudder-config-schema/issues/261)) ([e332c9b](https://github.com/rudderlabs/rudder-config-schema/commit/e332c9b791301fb9322e71a3bcd7d316449e8972))
* **s3-source:** added configuration for validation and cross account roles ([#162](https://github.com/rudderlabs/rudder-config-schema/issues/162)) ([0214723](https://github.com/rudderlabs/rudder-config-schema/commit/02147232546647b20ece0c5cf542222cbe3c9f80))
* sendgrid idetify and user deletion support ([#112](https://github.com/rudderlabs/rudder-config-schema/issues/112)) ([78d2f0d](https://github.com/rudderlabs/rudder-config-schema/commit/78d2f0d0cc1b84098341eb7938a3ae0566e67855))
* sendgrid idetify and user deletion support ([#127](https://github.com/rudderlabs/rudder-config-schema/issues/127)) ([ffb10c1](https://github.com/rudderlabs/rudder-config-schema/commit/ffb10c148bebe347822cc9948d0a26fe65ea6db4))
* subscription support in braze ([#175](https://github.com/rudderlabs/rudder-config-schema/issues/175)) ([b744a3c](https://github.com/rudderlabs/rudder-config-schema/commit/b744a3ce71d446195ebbd72f53ba3ba4d34248b2))
* support nested array ops braze ([#215](https://github.com/rudderlabs/rudder-config-schema/issues/215)) ([b7d592d](https://github.com/rudderlabs/rudder-config-schema/commit/b7d592d5f34455cdc22b957b45eaf53e98d0fb0f))
* update config for bing ads source release ([#217](https://github.com/rudderlabs/rudder-config-schema/issues/217)) ([d0884fa](https://github.com/rudderlabs/rudder-config-schema/commit/d0884fad309fdaf43a62dc7df06e3abaf7f9a4b5))
* update footernote in bigquery ([#189](https://github.com/rudderlabs/rudder-config-schema/issues/189)) ([b0af34c](https://github.com/rudderlabs/rudder-config-schema/commit/b0af34cbfa71ae0cac30406d9e6100e391ec0bd1))


### Bug Fixes

* add coming soon and remove from audience ([#139](https://github.com/rudderlabs/rudder-config-schema/issues/139)) ([d9d9a26](https://github.com/rudderlabs/rudder-config-schema/commit/d9d9a2632dd858bd1507c452613ce0d14a400842))
* add coming soon and remove from audience ([#143](https://github.com/rudderlabs/rudder-config-schema/issues/143)) ([638a957](https://github.com/rudderlabs/rudder-config-schema/commit/638a957f1d73f4a6862c3544857dd59914973663))
* add TestCase and update config for Podsights ([#92](https://github.com/rudderlabs/rudder-config-schema/issues/92)) ([4375261](https://github.com/rudderlabs/rudder-config-schema/commit/43752611be9ed2080085cffeb70e81eb91e71ab7))
* added onetrustCookieCategories in destinations schema ([#163](https://github.com/rudderlabs/rudder-config-schema/issues/163)) ([29daf01](https://github.com/rudderlabs/rudder-config-schema/commit/29daf014be7d8a7a04cce5b3858b10500a23ca63))
* braze update supportDedup key and footernote ([#176](https://github.com/rudderlabs/rudder-config-schema/issues/176)) ([95421be](https://github.com/rudderlabs/rudder-config-schema/commit/95421bef953df2f9262fb4e0380ec22656d3c757))
* content_type is customised for facebook offline conversions ([#57](https://github.com/rudderlabs/rudder-config-schema/issues/57)) ([b37c7e2](https://github.com/rudderlabs/rudder-config-schema/commit/b37c7e2c1e88f6d16b8a2dbd7b469e3dc910b44a))
* facebook_offline_conversions access token length issue ([#133](https://github.com/rudderlabs/rudder-config-schema/issues/133)) ([b9cc76e](https://github.com/rudderlabs/rudder-config-schema/commit/b9cc76ee522aa2bd02e6fd077c24c7873a68fed8))
* fix impact radius regex ([#258](https://github.com/rudderlabs/rudder-config-schema/issues/258)) ([8981b1b](https://github.com/rudderlabs/rudder-config-schema/commit/8981b1bf498a7cacf3c8255b361c6b6bc7f18320))
* fixed schema validation ([41536f4](https://github.com/rudderlabs/rudder-config-schema/commit/41536f4f08659474ec1eb128b8b47f534de9bfd0))
* footer note update on Podsights ([#98](https://github.com/rudderlabs/rudder-config-schema/issues/98)) ([cf4404e](https://github.com/rudderlabs/rudder-config-schema/commit/cf4404eb5498808bafa67473a2a24d8212b1c1b3))
* Footernode updated for Engage ([15526b7](https://github.com/rudderlabs/rudder-config-schema/commit/15526b79231bcaa7932559b699ab1fc33c1523a8))
* freshdesk spec file cleanup ([3bf07c3](https://github.com/rudderlabs/rudder-config-schema/commit/3bf07c3581ff5a4d0919cf1c0d5783e782c543f1))
* google-ads source config ([#169](https://github.com/rudderlabs/rudder-config-schema/issues/169)) ([a3c559c](https://github.com/rudderlabs/rudder-config-schema/commit/a3c559c16528e4feecb6a5ff4f614a2996a433f3))
* hubspot token hotfix ([e8f2b4c](https://github.com/rudderlabs/rudder-config-schema/commit/e8f2b4cee7be581a8ba53c85eebebb9fe8827a95))
* **integration:** adobe analytics - update regex for video events mapping to allow specific values ([#171](https://github.com/rudderlabs/rudder-config-schema/issues/171)) ([3133a4e](https://github.com/rudderlabs/rudder-config-schema/commit/3133a4e8dfc9687d80212aed6c0cd84ce1fe7fd9))
* marketo static list: removing preview tag ([#188](https://github.com/rudderlabs/rudder-config-schema/issues/188)) ([25983ef](https://github.com/rudderlabs/rudder-config-schema/commit/25983efbfa8f95f6ef3963963f6098f7e6f197ff))
* move files to new directory structure ([#257](https://github.com/rudderlabs/rudder-config-schema/issues/257)) ([e3a7ade](https://github.com/rudderlabs/rudder-config-schema/commit/e3a7aded5ea60af10c66ec3048a0890e94282c37))
* **qualaroo:** remove eventsList schema ([#87](https://github.com/rudderlabs/rudder-config-schema/issues/87)) ([9511a13](https://github.com/rudderlabs/rudder-config-schema/commit/9511a132d1e43f7a712fb5f75d411387ebca9cf5))
* remove iam role support ([e725fee](https://github.com/rudderlabs/rudder-config-schema/commit/e725fee95de7597e4b4075560af7bb9734e8fc1c))
* remove iam role support ([5032df2](https://github.com/rudderlabs/rudder-config-schema/commit/5032df2a2ea954902c934b0dbf0c8e1c24a3232a))
* removes oauth role from singer gsc ([#67](https://github.com/rudderlabs/rudder-config-schema/issues/67)) ([d73e610](https://github.com/rudderlabs/rudder-config-schema/commit/d73e6100881820733848210b79fe01a18e2e1b07))
* removes oauthrole for google sheets ([#117](https://github.com/rudderlabs/rudder-config-schema/issues/117)) ([1a56973](https://github.com/rudderlabs/rudder-config-schema/commit/1a5697392933d317e8e78b8bd4b69e300f6b9ba3))
* removing preview tag ([#167](https://github.com/rudderlabs/rudder-config-schema/issues/167)) ([ffb79ba](https://github.com/rudderlabs/rudder-config-schema/commit/ffb79ba1af2e495a421cdbaff6d316ce58a63722))
* rename files to the latest format ([efecaf7](https://github.com/rudderlabs/rudder-config-schema/commit/efecaf7652d828beaa90c6360362a43fd6a4bf30))
* resolve conflicts with master ([#107](https://github.com/rudderlabs/rudder-config-schema/issues/107)) ([fef97a8](https://github.com/rudderlabs/rudder-config-schema/commit/fef97a8560f6aaf1cc6daa3c9147d1d1ede5ddbd)), closes [#80](https://github.com/rudderlabs/rudder-config-schema/issues/80) [#100](https://github.com/rudderlabs/rudder-config-schema/issues/100) [#89](https://github.com/rudderlabs/rudder-config-schema/issues/89)
* revert bq changes ([#270](https://github.com/rudderlabs/rudder-config-schema/issues/270)) ([7775865](https://github.com/rudderlabs/rudder-config-schema/commit/77758655d8ac27d090a36fb2f316e3814bff5ac7))
* revert personalize config changed to remove iam role ([#122](https://github.com/rudderlabs/rudder-config-schema/issues/122)) ([6f66035](https://github.com/rudderlabs/rudder-config-schema/commit/6f6603582947d62253e2ffbc74719222ddbd8216))
* **satismeter:** set hidden to false ([#207](https://github.com/rudderlabs/rudder-config-schema/issues/207)) ([c4f6723](https://github.com/rudderlabs/rudder-config-schema/commit/c4f6723ed1e3e44663fe7c7a8e119a65d7f0f6b4))
* sendinblue regex ([#269](https://github.com/rudderlabs/rudder-config-schema/issues/269)) ([424ff9c](https://github.com/rudderlabs/rudder-config-schema/commit/424ff9c52e4342a14b94a236c66a3aee97cbc83f))
* **sendinblue:** schema ([#262](https://github.com/rudderlabs/rudder-config-schema/issues/262)) ([00bec4a](https://github.com/rudderlabs/rudder-config-schema/commit/00bec4a72bf15d90658a9d3ba41a745a2ca4cab0))
* **sendinblue:** schema ([#263](https://github.com/rudderlabs/rudder-config-schema/issues/263)) ([5888a95](https://github.com/rudderlabs/rudder-config-schema/commit/5888a95d570a50556e82e15894d4fac1dd1bf744))
* set preview to true (satismeter, axeptio, microsoft_clarity) ([#206](https://github.com/rudderlabs/rudder-config-schema/issues/206)) ([625d76f](https://github.com/rudderlabs/rudder-config-schema/commit/625d76fbd8508a387f5959e2af578a306481363a))
* singer salesforce new version ([#89](https://github.com/rudderlabs/rudder-config-schema/issues/89)) ([761ba3d](https://github.com/rudderlabs/rudder-config-schema/commit/761ba3dfa4207521ce6abca34c3820787784925c))
* supportedSourcesValidation in dbconfig ([#174](https://github.com/rudderlabs/rudder-config-schema/issues/174)) ([2112936](https://github.com/rudderlabs/rudder-config-schema/commit/2112936894e65b8c723b24641e1b4e7bb9291857))
* typo introduced while hiding facebook ads ([#238](https://github.com/rudderlabs/rudder-config-schema/issues/238)) ([1c5d860](https://github.com/rudderlabs/rudder-config-schema/commit/1c5d860d9fecb72a8ebd74ad68eb556f49db91ab))
* typo introduced while hiding facebook ads ([#238](https://github.com/rudderlabs/rudder-config-schema/issues/238)) ([2b63885](https://github.com/rudderlabs/rudder-config-schema/commit/2b63885619aace90910ac6c748c2e62cce236837))
* update google sheets image ([#194](https://github.com/rudderlabs/rudder-config-schema/issues/194)) ([3057183](https://github.com/rudderlabs/rudder-config-schema/commit/30571838340d13e64c5d7a28073321150f5a3a17))
* update singer_hubspot image ([68000da](https://github.com/rudderlabs/rudder-config-schema/commit/68000da2fed52f065ab938b75f308575cc51dbf9))
* updated factorsAI configs ([c586f5b](https://github.com/rudderlabs/rudder-config-schema/commit/c586f5b99db1738f746ada41d193589f09e7ecf6))
* updated flutter device mode support for destinations ADJ, AM, AppCenter, Braze, Firebase, Leanplum ([65bd102](https://github.com/rudderlabs/rudder-config-schema/commit/65bd102752a9a9bb93b0f8592125168c23ef0ec9))
* Webhook category added ([#81](https://github.com/rudderlabs/rudder-config-schema/issues/81)) ([0239729](https://github.com/rudderlabs/rudder-config-schema/commit/023972953dee246a6b60ecc2c3220bf8b94c45c1))
