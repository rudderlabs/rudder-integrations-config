# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [1.41.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.40.0...v1.41.0) (2023-07-10)


### Features

* add connectionMode check for datafile access token ([#751](https://github.com/rudderlabs/rudder-config-schema/issues/751)) ([2621d53](https://github.com/rudderlabs/rudder-config-schema/commit/2621d53f0ab0925f74135fa4a4f1cf111115bba3))
* **braze:** update preRequisite condition format based on config values ([#709](https://github.com/rudderlabs/rudder-config-schema/issues/709)) ([5f225b2](https://github.com/rudderlabs/rudder-config-schema/commit/5f225b26b64550f48103066a11a068f2c6e7e6eb))
* custom page event name amplitude ([#720](https://github.com/rudderlabs/rudder-config-schema/issues/720)) ([0998483](https://github.com/rudderlabs/rudder-config-schema/commit/0998483ef3b30d6d5dff6bce33295ca83754019a))
* factorsAI page,group support ([#724](https://github.com/rudderlabs/rudder-config-schema/issues/724)) ([957b6b8](https://github.com/rudderlabs/rudder-config-schema/commit/957b6b8b2ea87e44e75d58182edac956691bcf7c))


### Bug Fixes

* add enum for connectionMode instead of pattern ([#760](https://github.com/rudderlabs/rudder-config-schema/issues/760)) ([f00715d](https://github.com/rudderlabs/rudder-config-schema/commit/f00715da2f738b6b4400a611fb4049bc79ed1c99))
* added checks for required fields and pattern in schema ([#730](https://github.com/rudderlabs/rudder-config-schema/issues/730)) ([b1f0d68](https://github.com/rudderlabs/rudder-config-schema/commit/b1f0d68939be07a7c7555b4b442851124ecc1219))
* dynamicForm structure for sdk specific field ([#762](https://github.com/rudderlabs/rudder-config-schema/issues/762)) ([b6df1fd](https://github.com/rudderlabs/rudder-config-schema/commit/b6df1fd6488c9a67b74b9fc54c4899e455f947c3))
* fix schema generator script ([#750](https://github.com/rudderlabs/rudder-config-schema/issues/750)) ([f2bb48e](https://github.com/rudderlabs/rudder-config-schema/commit/f2bb48e8583d9c1c9fc1f7da9f238e53ce778765))
* make schema consistent with ui-config ([#678](https://github.com/rudderlabs/rudder-config-schema/issues/678)) ([50787b9](https://github.com/rudderlabs/rudder-config-schema/commit/50787b951155703f5321e0bee68a8b1301eae04a))
* schema and ui-config incosistency  ([#752](https://github.com/rudderlabs/rudder-config-schema/issues/752)) ([621c810](https://github.com/rudderlabs/rudder-config-schema/commit/621c8106fd2eb08a3d6aaaa58a6227dc355c2a62))
* schema generator script  ([#758](https://github.com/rudderlabs/rudder-config-schema/issues/758)) ([b68fb3b](https://github.com/rudderlabs/rudder-config-schema/commit/b68fb3bb7c115bf430cada8acf184676aa425a5e))
* schema validation inconsistency ([#686](https://github.com/rudderlabs/rudder-config-schema/issues/686)) ([a7434d2](https://github.com/rudderlabs/rudder-config-schema/commit/a7434d2190a5e1850e99c5c36bc28f6722b6892e))
* single select when mode is multiple and default pattern for dynamic custom form ([#732](https://github.com/rudderlabs/rudder-config-schema/issues/732)) ([2ac6eb9](https://github.com/rudderlabs/rudder-config-schema/commit/2ac6eb9c922ab8b174a25d095bdfb4be6ef18afb))

## [1.40.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.39.0...v1.40.0) (2023-07-04)


### Features

* ketch config added for a list of destinations ([108012a](https://github.com/rudderlabs/rudder-config-schema/commit/108012ae838f56d22b82782bc7640d287dc2a7f9))

## [1.39.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.38.1...v1.39.0) (2023-06-30)


### Features

* make twiiter ads visible in destination ([567791d](https://github.com/rudderlabs/rudder-config-schema/commit/567791d0e376f1afb9ec74713d21b4899ca82be7))


### Bug Fixes

* update regex to allow digit 0 for accountId ([#745](https://github.com/rudderlabs/rudder-config-schema/issues/745)) ([86c3160](https://github.com/rudderlabs/rudder-config-schema/commit/86c3160c12387ce1db0cd5668194cbd60f598379))

### [1.38.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.38.0...v1.38.1) (2023-06-28)


### Bug Fixes

* gav4 metrics and dimension configuration ([3c11edb](https://github.com/rudderlabs/rudder-config-schema/commit/3c11edbe399ad01c851ad7dbc65f8828c51321ba))

## [1.38.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.37.3...v1.38.0) (2023-06-23)


### Features

* **ga4:** enhance support for debug_view in device and hybrid connection modes ([#696](https://github.com/rudderlabs/rudder-config-schema/issues/696)) ([135dc81](https://github.com/rudderlabs/rudder-config-schema/commit/135dc81438bbf6cea02ac6fd67c79a6493fddf78))
* **klaviyo:** update label and footer note for primary identifier toggle ([#721](https://github.com/rudderlabs/rudder-config-schema/issues/721)) ([a364f93](https://github.com/rudderlabs/rudder-config-schema/commit/a364f9349683c4d2862986cbd4f27d653b921fda))
* **optimizely_fullstack:** update configuration and onboarded on new UI ([#706](https://github.com/rudderlabs/rudder-config-schema/issues/706)) ([af291e3](https://github.com/rudderlabs/rudder-config-schema/commit/af291e3c420bb2789831764f47d4db2838ddb42f))
* **profiles:** updated Profiles project Github URLs ([#715](https://github.com/rudderlabs/rudder-config-schema/issues/715)) ([646664c](https://github.com/rudderlabs/rudder-config-schema/commit/646664c734d0315552c0fbbf212d3e91b2ddf750))
* twiiter web conversions ([#694](https://github.com/rudderlabs/rudder-config-schema/issues/694)) ([7f2329b](https://github.com/rudderlabs/rudder-config-schema/commit/7f2329b9bbd4435860f4de2180155b8270f4f561))


### Bug Fixes

* diff to be printed properly in schema ci validation ([#727](https://github.com/rudderlabs/rudder-config-schema/issues/727)) ([c3edd76](https://github.com/rudderlabs/rudder-config-schema/commit/c3edd7698885e72a2c87d65196b853bcf1b09be7))
* pattern generalise function and schema diff in schema generator script ([#712](https://github.com/rudderlabs/rudder-config-schema/issues/712)) ([1115a0a](https://github.com/rudderlabs/rudder-config-schema/commit/1115a0a72e6e7ad8dcfd24bb5f34689d8a3e85f8))

### [1.37.3](https://github.com/rudderlabs/rudder-config-schema/compare/v1.37.2...v1.37.3) (2023-06-21)


### Bug Fixes

* updat git URLs and add hidden flag ([a93ce6c](https://github.com/rudderlabs/rudder-config-schema/commit/a93ce6cbd56a35011062ddd460e5c00a29d727fc))
* updates Profiles project Github URLs ([5e9684a](https://github.com/rudderlabs/rudder-config-schema/commit/5e9684a0426c81e2f7abf24a3a7ba87976f9cbc0))

### [1.37.2](https://github.com/rudderlabs/rudder-config-schema/compare/v1.37.1...v1.37.2) (2023-06-20)

### [1.37.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.37.0...v1.37.1) (2023-06-19)


### Bug Fixes

* updates intercom to v7.0.1 ([a820ae3](https://github.com/rudderlabs/rudder-config-schema/commit/a820ae381e9d6cc068fb14d1f446e26a3a74c186))

## [1.37.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.36.0...v1.37.0) (2023-06-12)


### Features

* **klaviyo:** update ui-config based on new api version ([#710](https://github.com/rudderlabs/rudder-config-schema/issues/710)) ([d1c571e](https://github.com/rudderlabs/rudder-config-schema/commit/d1c571e517a988e8ba49698ff410ab5ea1e02a84))
* onboard tiktok device mode integration ([#668](https://github.com/rudderlabs/rudder-config-schema/issues/668)) ([3f2e2cd](https://github.com/rudderlabs/rudder-config-schema/commit/3f2e2cdce1f4f97f2f5c01459b376fbe592928c7))


### Bug Fixes

* anyOf to be array and schema diff for allOf, anyOf in schema generator script ([#701](https://github.com/rudderlabs/rudder-config-schema/issues/701)) ([6086e4c](https://github.com/rudderlabs/rudder-config-schema/commit/6086e4ce39461c048cc5c4cd8c962692f8f552c7))
* eventMapping to allow only dropdown values ([#702](https://github.com/rudderlabs/rudder-config-schema/issues/702)) ([d2cece7](https://github.com/rudderlabs/rudder-config-schema/commit/d2cece79d893da8e0ae80483932a676b542f90d6))

## [1.36.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.35.0...v1.36.0) (2023-06-06)


### Features

* add support for wht lib project defitions ([#659](https://github.com/rudderlabs/rudder-config-schema/issues/659)) ([337e978](https://github.com/rudderlabs/rudder-config-schema/commit/337e9783ad38e68bbec23ee7343f2764bef6bd94))
* added Ketch integration for a list of destinations ([#685](https://github.com/rudderlabs/rudder-config-schema/issues/685)) ([526ee90](https://github.com/rudderlabs/rudder-config-schema/commit/526ee90fad75423b724b66c1ffc00b7cc00ffa7c))
* **pinterest:** update footer note ([9c3165b](https://github.com/rudderlabs/rudder-config-schema/commit/9c3165b36ccc7c01fc07efd6b2f6ce35ab053562))

## [1.35.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.34.0...v1.35.0) (2023-06-02)


### Features

* **shopify:** add disableClientSideIdentifier field in uiConfig ([#698](https://github.com/rudderlabs/rudder-config-schema/issues/698)) ([3f84471](https://github.com/rudderlabs/rudder-config-schema/commit/3f84471a3848d4862013c58eb23a50dd71c5d2c7))

## [1.34.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.33.2...v1.34.0) (2023-05-30)


### Features

* mixpanel deletion api ([#680](https://github.com/rudderlabs/rudder-config-schema/issues/680)) ([11dac5a](https://github.com/rudderlabs/rudder-config-schema/commit/11dac5a91fd873470eeb0c1cbf7e2ee4bfd19fd1))
* remove hidden flag for dynamic yield destination ([#687](https://github.com/rudderlabs/rudder-config-schema/issues/687)) ([b89dd82](https://github.com/rudderlabs/rudder-config-schema/commit/b89dd8236f9407fc8839c955b595f191ff347023))
* remove property mapping for other standard events in fb pixel ([#630](https://github.com/rudderlabs/rudder-config-schema/issues/630)) ([0c71e88](https://github.com/rudderlabs/rudder-config-schema/commit/0c71e88321e192ce9fe9aefca4a6a98cde42e1c6))


### Bug Fixes

* **bingads_audience:** add hashEmail field and enable cdkv2 ([#691](https://github.com/rudderlabs/rudder-config-schema/issues/691)) ([9062017](https://github.com/rudderlabs/rudder-config-schema/commit/90620172a58a8feef83c642f172f41ee760be8b4))
* s3 configs for access keys and iam roles for warehouse destinations ([#677](https://github.com/rudderlabs/rudder-config-schema/issues/677)) ([b48f2b0](https://github.com/rudderlabs/rudder-config-schema/commit/b48f2b0fab282b3c2fec660c70cf2c1e274d6abc))

### [1.33.2](https://github.com/rudderlabs/rudder-config-schema/compare/v1.33.1...v1.33.2) (2023-05-26)


### Bug Fixes

* update klaviyo to include a back-look window for events stream ([ae57fcc](https://github.com/rudderlabs/rudder-config-schema/commit/ae57fcc138cdfc1e2b44a470282b48e2943e6794))

### [1.33.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.33.0...v1.33.1) (2023-05-23)


### Bug Fixes

* hide dynamic yield ([ba9ee70](https://github.com/rudderlabs/rudder-config-schema/commit/ba9ee70882f464ba895fd0bfb5c4d8731ba1eee8))

## [1.33.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.32.0...v1.33.0) (2023-05-23)


### Features

* **google ads:** enable conversion label option ([#663](https://github.com/rudderlabs/rudder-config-schema/issues/663)) ([94b2858](https://github.com/rudderlabs/rudder-config-schema/commit/94b28581c46a0a12c31e54864fda155deab47a38))
* onboard dynamic yield destination ([#552](https://github.com/rudderlabs/rudder-config-schema/issues/552)) ([bb23ddd](https://github.com/rudderlabs/rudder-config-schema/commit/bb23ddd284f55818b60aaf858dcbd6bff14bc73a))


### Bug Fixes

* **ga4:** update field label and description ([#648](https://github.com/rudderlabs/rudder-config-schema/issues/648)) ([abd4f8c](https://github.com/rudderlabs/rudder-config-schema/commit/abd4f8c7a968bcecd914aa95100167b4f4131425))

## [1.32.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.31.1...v1.32.0) (2023-05-18)


### Features

* move Rockerbox to new UI form builder ([#660](https://github.com/rudderlabs/rudder-config-schema/issues/660)) ([110b690](https://github.com/rudderlabs/rudder-config-schema/commit/110b6900d80a34da07d32d81a5855206ea7cde06))

### [1.31.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.31.0...v1.31.1) (2023-05-17)


### Bug Fixes

* fix ui-config and schema for avroSchemas and embedAvroSchemaID fields in kafka destination ([#657](https://github.com/rudderlabs/rudder-config-schema/issues/657)) ([a390cc0](https://github.com/rudderlabs/rudder-config-schema/commit/a390cc041e88d6f4b04cef859689a8c83c7982fc))

## [1.31.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.30.5...v1.31.0) (2023-05-15)


### Features

* custom host for fullstory ([#619](https://github.com/rudderlabs/rudder-config-schema/issues/619)) ([52f1ad1](https://github.com/rudderlabs/rudder-config-schema/commit/52f1ad1e5a51874b8ccbb19ec668993d46219238))
* **GA4:** override configuration for client_id and session_id in GA hybrid mode ([#607](https://github.com/rudderlabs/rudder-config-schema/issues/607)) ([7d2acf6](https://github.com/rudderlabs/rudder-config-schema/commit/7d2acf6ddcdbe5e13e56f430709b6c8ee82ba84d))
* mixpanel deletion api ([#631](https://github.com/rudderlabs/rudder-config-schema/issues/631)) ([8c0d632](https://github.com/rudderlabs/rudder-config-schema/commit/8c0d6325de1e7462c00b7d4063278f798477ae78))
* support event filtering in a scalable way for hybrid mode ([#524](https://github.com/rudderlabs/rudder-config-schema/issues/524)) ([f8ef967](https://github.com/rudderlabs/rudder-config-schema/commit/f8ef9677521752c5bf8060050e22b10d084cb796))

### [1.30.5](https://github.com/rudderlabs/rudder-config-schema/compare/v1.30.4...v1.30.5) (2023-05-13)


### Bug Fixes

* updates stripe to 6.3.4 ([580ddaa](https://github.com/rudderlabs/rudder-config-schema/commit/580ddaa84c2b8f184792f5eda0a7a74dc68d7309))

### [1.30.4](https://github.com/rudderlabs/rudder-config-schema/compare/v1.30.3...v1.30.4) (2023-05-13)


### Bug Fixes

* updates stripe image to v6.3.3 ([05cf4f3](https://github.com/rudderlabs/rudder-config-schema/commit/05cf4f3811c9d242c011905537f0aa7ddc9af379))

### [1.30.3](https://github.com/rudderlabs/rudder-config-schema/compare/v1.30.2...v1.30.3) (2023-05-12)


### Bug Fixes

* fixes stripe api version issue ([471a8c9](https://github.com/rudderlabs/rudder-config-schema/commit/471a8c9aa5e13d35e37be6bfd6399798db4f360a))

### [1.30.2](https://github.com/rudderlabs/rudder-config-schema/compare/v1.30.1...v1.30.2) (2023-05-12)


### Bug Fixes

* resolve discrepancies in amplitude config files ([#637](https://github.com/rudderlabs/rudder-config-schema/issues/637)) ([543a9f6](https://github.com/rudderlabs/rudder-config-schema/commit/543a9f6121c5dae15628994dd92b7fdb90d512bf))

### [1.30.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.30.0...v1.30.1) (2023-05-10)

## [1.30.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.29.0...v1.30.0) (2023-05-09)


### Features

* alias call braze ([#625](https://github.com/rudderlabs/rudder-config-schema/issues/625)) ([b15cc40](https://github.com/rudderlabs/rudder-config-schema/commit/b15cc40c54285fa87790b705a9d083d6c1ce679c))
* onboard new source formsort  ([#606](https://github.com/rudderlabs/rudder-config-schema/issues/606)) ([6560241](https://github.com/rudderlabs/rudder-config-schema/commit/6560241a81818d0490aa0d68e884e6cd04930add))

### [1.28.3](https://github.com/rudderlabs/rudder-config-schema/compare/v1.28.2...v1.28.3) (2023-05-05)


### Features

* added blank audience support for criteo and fb audience, added warehouse settings for criteo ([#543](https://github.com/rudderlabs/rudder-config-schema/issues/543)) ([e0b64cc](https://github.com/rudderlabs/rudder-config-schema/commit/e0b64ccd2546685a2aa70e9234f43948f00dcfff))
* conversion label option added for google ads conversion events ([#602](https://github.com/rudderlabs/rudder-config-schema/issues/602)) ([80ffe00](https://github.com/rudderlabs/rudder-config-schema/commit/80ffe00e3900b48eab9ab88d70856a9ac0378741))
* **destination:** onboard bing ads audience destination ([#525](https://github.com/rudderlabs/rudder-config-schema/issues/525)) ([f7f76f2](https://github.com/rudderlabs/rudder-config-schema/commit/f7f76f26d72ce0ea48290750cc8e75881a90a8a5))
* enable group for intercom ([#583](https://github.com/rudderlabs/rudder-config-schema/issues/583)) ([0bef2dd](https://github.com/rudderlabs/rudder-config-schema/commit/0bef2ddded00ec95c9800916ab314798c5df1308))
* enable pinterest cdk ([#603](https://github.com/rudderlabs/rudder-config-schema/issues/603)) ([4465335](https://github.com/rudderlabs/rudder-config-schema/commit/4465335c82d3f12d860376849bd6f3ba663e8392))
* kafka via ssh redo reverted change ([#610](https://github.com/rudderlabs/rudder-config-schema/issues/610)) ([7dab511](https://github.com/rudderlabs/rudder-config-schema/commit/7dab511f132fe0463ee8aca34236f3d9a37252f8))
* singer marketo ([#614](https://github.com/rudderlabs/rudder-config-schema/issues/614)) ([6603c79](https://github.com/rudderlabs/rudder-config-schema/commit/6603c798ffa070555084d40ae71f9121e0b0b364))


### Bug Fixes

* **fb_custom_audience:** remove skip verify checkbox ([#612](https://github.com/rudderlabs/rudder-config-schema/issues/612)) ([8ddeafd](https://github.com/rudderlabs/rudder-config-schema/commit/8ddeafd76380b886ed901ad5c00db212d5f99dcc))
* removed adAccountId from shcema ([#618](https://github.com/rudderlabs/rudder-config-schema/issues/618)) ([d074a32](https://github.com/rudderlabs/rudder-config-schema/commit/d074a3279ff6a3aad0cbe86c2b4b17762c8f43ec))

## [1.29.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.28.2...v1.29.0) (2023-05-05)


### Features

* added blank audience support for criteo_audience ([8b2f76c](https://github.com/rudderlabs/rudder-config-schema/commit/8b2f76c1e7f153735b5a5e47ced94a8f14bc3597))
* added key for supporting blank audience for fb audience ([3ad957b](https://github.com/rudderlabs/rudder-config-schema/commit/3ad957b5c52d14721ea789642e09cc05ba332202))

### [1.28.2](https://github.com/rudderlabs/rudder-config-schema/compare/v1.28.1...v1.28.2) (2023-05-03)


### Bug Fixes

* empty schema for kafka to override config-be validator ([576c59a](https://github.com/rudderlabs/rudder-config-schema/commit/576c59a8c4ab008364f3e94d2f3c9bd289154506))
* updates klaviyo to 6.2.5 ([3a593ad](https://github.com/rudderlabs/rudder-integrations-config/pull/609/commits/3a593adb47b0897aa0dc91a3132a928ee45f2593))

### [1.28.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.28.0...v1.28.1) (2023-05-02)

## [1.28.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.27.0...v1.28.0) (2023-05-02)


### Features

* added audience support for criteo_audience ([#598](https://github.com/rudderlabs/rudder-config-schema/issues/598)) ([cbaa120](https://github.com/rudderlabs/rudder-config-schema/commit/cbaa120255ee2a827e8243c24e51514904eab05d))
* modified to return sshPublicKey to end user ([#585](https://github.com/rudderlabs/rudder-config-schema/issues/585)) ([fe9e125](https://github.com/rudderlabs/rudder-config-schema/commit/fe9e125dc966818b4db8f592f778eb0b5105e012))


### Bug Fixes

* **GA4:** updated broken link for capture page view ([#597](https://github.com/rudderlabs/rudder-config-schema/issues/597)) ([95f9a7f](https://github.com/rudderlabs/rudder-config-schema/commit/95f9a7f739702c5435d806f0007ae9b519cc93e6))

## [1.27.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.26.2...v1.27.0) (2023-04-26)


### Features

* hide shopify source from UI ([64b867c](https://github.com/rudderlabs/rudder-config-schema/commit/64b867c9be7de41634c4bfe383e2bfa1a59377ca))

### [1.26.2](https://github.com/rudderlabs/rudder-config-schema/compare/v1.26.1...v1.26.2) (2023-04-25)


### Bug Fixes

* revert kafka over ssh change via control-plane ([#591](https://github.com/rudderlabs/rudder-config-schema/issues/591)) ([ed835b8](https://github.com/rudderlabs/rudder-config-schema/commit/ed835b849c18a3a5db1f08caff96bacee608f9d9))

### [1.26.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.26.0...v1.26.1) (2023-04-25)


### Bug Fixes

* **pinterest:** remove cdk flag ([#587](https://github.com/rudderlabs/rudder-config-schema/issues/587)) ([898f17a](https://github.com/rudderlabs/rudder-config-schema/commit/898f17a1f09611c4bae15d1209fbb8fd567ceb27))

## [1.26.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.25.0...v1.26.0) (2023-04-25)


### Features

* **ga4:** override gtag session_id configuration option ([#559](https://github.com/rudderlabs/rudder-config-schema/issues/559)) ([14ea841](https://github.com/rudderlabs/rudder-config-schema/commit/14ea841d8db53fd4f5d2a941f4942d10f5e60581))
* **ga4:** update ui field name && description ([429b9f3](https://github.com/rudderlabs/rudder-config-schema/commit/429b9f3dcaff5ce3b4b785e78221d8eed6e1a9e4))
* move hardcoded ga dimensions and metrics ([#523](https://github.com/rudderlabs/rudder-config-schema/issues/523)) ([9c61fb3](https://github.com/rudderlabs/rudder-config-schema/commit/9c61fb31df5ccce083162faae66d8fa9c0dc7583))
* onboard leanplum destination new ui config ([#475](https://github.com/rudderlabs/rudder-config-schema/issues/475)) ([26edab1](https://github.com/rudderlabs/rudder-config-schema/commit/26edab1d753a9e8bf7e993dbdaa76883d2fdd738))
* **pinterest:** version update ([#546](https://github.com/rudderlabs/rudder-config-schema/issues/546)) ([dd245b8](https://github.com/rudderlabs/rudder-config-schema/commit/dd245b899fa00c89dee0b4dfff72317d20961efb))
* support connection to kafka over ssh for growth customer ([#535](https://github.com/rudderlabs/rudder-config-schema/issues/535)) ([d18e45a](https://github.com/rudderlabs/rudder-config-schema/commit/d18e45a60d4a26901db42ac1905a5406f9f67b65))


### Bug Fixes

* renaming blacklist to denylist and whitelist to allowlist ([#581](https://github.com/rudderlabs/rudder-config-schema/issues/581)) ([4f9a9f7](https://github.com/rudderlabs/rudder-config-schema/commit/4f9a9f78203d743e2c16785ad23ea68f13e5382b))

## [1.25.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.24.1...v1.25.0) (2023-04-24)


### Features

* **pinterest:** update secretKeys ([#575](https://github.com/rudderlabs/rudder-config-schema/issues/575)) ([1ec812e](https://github.com/rudderlabs/rudder-config-schema/commit/1ec812eeef874eca2239f7fbfc336afce99c075f))
* **pinterest:** version update  ([#573](https://github.com/rudderlabs/rudder-config-schema/issues/573)) ([7ca6c71](https://github.com/rudderlabs/rudder-config-schema/commit/7ca6c716d96a7ec53190698adeb911a21d2cfb04))

### [1.24.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.24.0...v1.24.1) (2023-04-21)


### Bug Fixes

* revert displayNames for BingAds, GA, Kissmetrics ([b5645d5](https://github.com/rudderlabs/rudder-config-schema/commit/b5645d590bda0ce7ae89daadbe57cc78dbb96680))

## [1.24.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.23.1...v1.24.0) (2023-04-20)


### Features

* **ga4:** override gtag session_id configuration option ([#565](https://github.com/rudderlabs/rudder-config-schema/issues/565)) ([92813a3](https://github.com/rudderlabs/rudder-config-schema/commit/92813a3c6e1d73c0a8581938c043dd0aefc376fa))

### [1.23.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.23.0...v1.23.1) (2023-04-19)


### Bug Fixes

* updates shopify to 6.2.3 ([08e41d2](https://github.com/rudderlabs/rudder-config-schema/commit/08e41d2d46d4a01fd53be57041437d23a664fa36))

## [1.23.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.22.1...v1.23.0) (2023-04-17)


### Features

* braze new UI ([#542](https://github.com/rudderlabs/rudder-config-schema/issues/542)) ([a8fa48c](https://github.com/rudderlabs/rudder-config-schema/commit/a8fa48c1f1773cb1f086b55f0bef77ce19593e50))
* **mixpanel:** add identity merge dropdown ([#517](https://github.com/rudderlabs/rudder-config-schema/issues/517)) ([0113e4b](https://github.com/rudderlabs/rudder-config-schema/commit/0113e4bb508d73ede5bbfa5df91ab0af4dc85d9e))


### Bug Fixes

* **cdk v2:** putting webhook back to cdk v2 ([#556](https://github.com/rudderlabs/rudder-config-schema/issues/556)) ([d47f1b7](https://github.com/rudderlabs/rudder-config-schema/commit/d47f1b707eb509887699d576936b0b46f833826d))
* **GA4:** remove send_to parameter as configurable option  ([#522](https://github.com/rudderlabs/rudder-config-schema/issues/522)) ([f07ab0f](https://github.com/rudderlabs/rudder-config-schema/commit/f07ab0f7fda59af78b779ab106ed3a3896aaec5b))

### [1.22.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.22.0...v1.22.1) (2023-04-17)


### Bug Fixes

* **cdk v2:** temporarily moving webhook from cdk v2 to native ([de7a6f4](https://github.com/rudderlabs/rudder-config-schema/commit/de7a6f4bc4710a294ee53cb5d6330309b1d3352d))

## [1.22.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.21.3...v1.22.0) (2023-04-13)


### Features

* braze UI update ([#544](https://github.com/rudderlabs/rudder-config-schema/issues/544)) ([e48f509](https://github.com/rudderlabs/rudder-config-schema/commit/e48f509f73e52eb51b3c16f924992e2a46032faa))

### [1.21.3](https://github.com/rudderlabs/rudder-config-schema/compare/v1.21.2...v1.21.3) (2023-04-12)


### Bug Fixes

* set supportsDestinationSyncMode flag to false ([5981c94](https://github.com/rudderlabs/rudder-config-schema/commit/5981c94a02c42d000f57df70c1c94f2c1be5005f))

### [1.21.2](https://github.com/rudderlabs/rudder-config-schema/compare/v1.21.1...v1.21.2) (2023-04-12)

### [1.21.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.21.0...v1.21.1) (2023-04-11)


### Bug Fixes

* updates amplitude to 5.3.0 ([e1fb0e8](https://github.com/rudderlabs/rudder-config-schema/commit/e1fb0e8a0d58998a4f33e20f0456ea37076686de))
* updates hubspot to 6.2.4 ([ba48524](https://github.com/rudderlabs/rudder-config-schema/commit/ba48524d36c239156d459ad9cebd1a638bd42a26))

## [1.21.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.20.4...v1.21.0) (2023-04-11)


### Features

* enhancement gaoc store conversion ([#473](https://github.com/rudderlabs/rudder-config-schema/issues/473)) ([c0324b4](https://github.com/rudderlabs/rudder-config-schema/commit/c0324b4f56822cdf4b0140cbb1a445b4411ba846))


### Bug Fixes

* make Ad Account id field optional for FB Custom Audience ([#521](https://github.com/rudderlabs/rudder-config-schema/issues/521)) ([15136dd](https://github.com/rudderlabs/rudder-config-schema/commit/15136dde0bfb00991e8ecf515ea07382c1d24b26))

### [1.20.4](https://github.com/rudderlabs/rudder-config-schema/compare/v1.20.3...v1.20.4) (2023-04-06)


### Bug Fixes

* copy update to ga4 ([#518](https://github.com/rudderlabs/rudder-config-schema/issues/518)) ([7c52d57](https://github.com/rudderlabs/rudder-config-schema/commit/7c52d57f717c50a03795c0d1f699856fc15bcf57))

### [1.20.3](https://github.com/rudderlabs/rudder-config-schema/compare/v1.20.2...v1.20.3) (2023-04-06)


### Bug Fixes

* added device mode support for a flutter source to appsflyer destination ([#514](https://github.com/rudderlabs/rudder-config-schema/issues/514)) ([02a6d84](https://github.com/rudderlabs/rudder-config-schema/commit/02a6d843e7fd7b62efd73249415b4c9c275d6a87))

### [1.20.2](https://github.com/rudderlabs/rudder-config-schema/compare/v1.20.1...v1.20.2) (2023-04-05)

### [1.20.1](https://github.com/rudderlabs/rudder-config-schema/compare/v1.20.0...v1.20.1) (2023-04-04)

## [1.20.0](https://github.com/rudderlabs/rudder-config-schema/compare/v1.19.0...v1.20.0) (2023-04-04)


### Features

* **klaviyo:** make private API kay mandatory ([#501](https://github.com/rudderlabs/rudder-config-schema/issues/501)) ([a2d26b8](https://github.com/rudderlabs/rudder-config-schema/commit/a2d26b8d3a1e8faa463585545411b329ee1b950e))


### Bug Fixes

* impact error message and test update ([#499](https://github.com/rudderlabs/rudder-config-schema/issues/499)) ([de7d78f](https://github.com/rudderlabs/rudder-config-schema/commit/de7d78f67554f16c35bb0509fe0fd8f37a6adca2))

## [1.19.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.18.1...v1.19.0) (2023-04-04)


### Features

* added sync type, supproted sources, and support vdm ([#455](https://github.com/rudderlabs/rudder-config-schema/issues/455)) ([635dce1](https://github.com/rudderlabs/rudder-config-schema/commit/635dce1b34481a58695d9e44e89d480f3a1d0888))
* **goole_ads:** add allow enhaced conversions toggle ([#474](https://github.com/rudderlabs/rudder-config-schema/issues/474)) ([d71c9d8](https://github.com/rudderlabs/rudder-config-schema/commit/d71c9d861309e5a7ab9f0b7550dc9fce2ad3dfa2))
* **integrations:** onboarding webhook CDKv2 for hosted ([#477](https://github.com/rudderlabs/rudder-config-schema/issues/477)) ([08710ff](https://github.com/rudderlabs/rudder-config-schema/commit/08710ff3528621a279781e34d9a6739f6ad85d15))


### Bug Fixes

* removes extract support for cloud destinations ([#494](https://github.com/rudderlabs/rudder-config-schema/issues/494)) ([20f989d](https://github.com/rudderlabs/rudder-config-schema/commit/20f989d3b2ebed552068da6c66adc8d809a9aa5c))

### [1.18.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.18.0...1.18.1) (2023-03-28)


### Bug Fixes

* udate zendesk support source  image version ([959ea67](https://github.com/rudderlabs/rudder-config-schema/commit/959ea67b71085bef93f84dfcdd7001185e976d47))

## [1.18.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.17.1...1.18.0) (2023-03-28)


### Bug Fixes

* **optimizely_fullstack:** filter identify events  ([#482](https://github.com/rudderlabs/rudder-config-schema/issues/482)) ([3dcc917](https://github.com/rudderlabs/rudder-config-schema/commit/3dcc917730fb8c2a3d0e8c0fb31d993b23289b97))

### [1.17.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.17.0...1.17.1) (2023-03-27)

## [1.17.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.16.0...1.17.0) (2023-03-23)


### Features

* moved oneTrustCookieCategories field to defaultConfig ([#456](https://github.com/rudderlabs/rudder-config-schema/issues/456)) ([eccf357](https://github.com/rudderlabs/rudder-config-schema/commit/eccf35751916879255dd25848a34912b13298135))
* moved oneTrustCookieCategories field to defaultConfig ([#456](https://github.com/rudderlabs/rudder-config-schema/issues/456)) ([f527af7](https://github.com/rudderlabs/rudder-config-schema/commit/f527af765254598c0670bed9e43509ff174271a7))
* **snowflake:** drop cloud provider from src ui-config ([#449](https://github.com/rudderlabs/rudder-config-schema/issues/449)) ([fc6d33c](https://github.com/rudderlabs/rudder-config-schema/commit/fc6d33c2d4b4b201fa9ef02fc54a75f9e695bad1))


### Bug Fixes

* destination name revamp to latest standard ([#459](https://github.com/rudderlabs/rudder-config-schema/issues/459)) ([44b243b](https://github.com/rudderlabs/rudder-config-schema/commit/44b243b14cb8a9e2608f321845b5555297b4d4b1))

## [1.16.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.15.1...1.16.0) (2023-03-21)


### Features

* **clevertap:** add support for indonesia and middle east regions ([#460](https://github.com/rudderlabs/rudder-config-schema/issues/460)) ([205ceb5](https://github.com/rudderlabs/rudder-config-schema/commit/205ceb5cfb94b67ee6eed59c4e731fa91f503b75))
* remove beta tag from courier ([#465](https://github.com/rudderlabs/rudder-config-schema/issues/465)) ([114b164](https://github.com/rudderlabs/rudder-config-schema/commit/114b164612bebaa6c666fcb84ecfe95967044f36))

### [1.15.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.15.0...1.15.1) (2023-03-20)

## [1.15.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.14.0...1.15.0) (2023-03-14)


### Features

* default role based auth to true for all AWS dests using roleBaseAuth ([#447](https://github.com/rudderlabs/rudder-config-schema/issues/447)) ([f2925cc](https://github.com/rudderlabs/rudder-config-schema/commit/f2925cca2a590d9c22d1cdc51e055a9d0cc9dea2))


### Bug Fixes

* remove dest pipedrive by using hidden flag ([#453](https://github.com/rudderlabs/rudder-config-schema/issues/453)) ([bd8cb89](https://github.com/rudderlabs/rudder-config-schema/commit/bd8cb89820438685becb9f7cafbc3f5064b34b66))

## [1.14.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.13.1...1.14.0) (2023-03-13)


### Features

* remove supportedMessageTypes for Firehose ([#450](https://github.com/rudderlabs/rudder-config-schema/issues/450)) ([623f897](https://github.com/rudderlabs/rudder-config-schema/commit/623f897fcb348465c520e61113b7e0dc37b5c547))

### [1.13.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.13.0...1.13.1) (2023-03-13)


### Features

* enable moengage source ([#448](https://github.com/rudderlabs/rudder-config-schema/issues/448)) ([f8b2320](https://github.com/rudderlabs/rudder-config-schema/commit/f8b23206c75aca187de5c837766d9d0862e011f2))
* ga4 new ui layout ([#389](https://github.com/rudderlabs/rudder-config-schema/issues/389)) ([c03ce2f](https://github.com/rudderlabs/rudder-config-schema/commit/c03ce2f6690ff90a442668ccc26ea328010aaf70))
* mautic: support self hosted instance ([#424](https://github.com/rudderlabs/rudder-config-schema/issues/424)) ([afda253](https://github.com/rudderlabs/rudder-config-schema/commit/afda253d3d7fe73297caf10189e7a95e132f06f4))
* moengage alias call ([#445](https://github.com/rudderlabs/rudder-config-schema/issues/445)) ([33e3965](https://github.com/rudderlabs/rudder-config-schema/commit/33e3965d63bc77a94c3a429860d5342003f6e113))
* moving sfmc to router ([#443](https://github.com/rudderlabs/rudder-config-schema/issues/443)) ([ab0255d](https://github.com/rudderlabs/rudder-config-schema/commit/ab0255d5b1fc4d4b314f4814757e0a9cc84d9bcf))

## [1.13.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.12.0...1.13.0) (2023-03-09)


### Features

* add missing schema and ui validations for top 40 destination ([#355](https://github.com/rudderlabs/rudder-config-schema/issues/355)) ([050f3da](https://github.com/rudderlabs/rudder-config-schema/commit/050f3daf577d9baa952ee93d5696e3c16358d17b))
* **AM:** add supportedConnectionModes   ([#438](https://github.com/rudderlabs/rudder-config-schema/issues/438)) ([09b119c](https://github.com/rudderlabs/rudder-config-schema/commit/09b119c1d70d9f87b696b36b0be5328471f2b53f))


### Bug Fixes

* missing consent settings for FB ([fdeca41](https://github.com/rudderlabs/rudder-config-schema/commit/fdeca4101aa79177d83bc831792e8f0362a4caf9))
* missing consent settings schema for FB ([524a8b1](https://github.com/rudderlabs/rudder-config-schema/commit/524a8b1393c450d2cbbd4e46ef33016d78cb89c4))
* missing schema testcase for FB ([5376a0f](https://github.com/rudderlabs/rudder-config-schema/commit/5376a0f387049361426e074e0d709a4f09ae0f50))

## [1.12.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.11.1...1.12.0) (2023-03-07)


### Features

* introduced external_id flag  ([#425](https://github.com/rudderlabs/rudder-config-schema/issues/425)) ([47b2ae3](https://github.com/rudderlabs/rudder-config-schema/commit/47b2ae3af21ebcf81305d5f03c85143a7605cfd7))
* moved oneTrustCookieCategories to default config and made available for cloud mode ([#403](https://github.com/rudderlabs/rudder-config-schema/issues/403)) ([12c7ee8](https://github.com/rudderlabs/rudder-config-schema/commit/12c7ee82457ffda2c1d2299cf3ef2e235a941340))


### Bug Fixes

* fbPixel UI Config ([#435](https://github.com/rudderlabs/rudder-config-schema/issues/435)) ([79e4b3d](https://github.com/rudderlabs/rudder-config-schema/commit/79e4b3d348a98de50337ae3c626de3bcac6e2a3e))
* reverting an unwanted change, adding connectionMode field back to uiConfig ([#433](https://github.com/rudderlabs/rudder-config-schema/issues/433)) ([a6a07f5](https://github.com/rudderlabs/rudder-config-schema/commit/a6a07f5da55f960f805ee21365d86e5e74f582c7))
* singer-shopify image version ([#432](https://github.com/rudderlabs/rudder-config-schema/issues/432)) ([c715761](https://github.com/rudderlabs/rudder-config-schema/commit/c715761ebea1ca2d830a69c7e7c52e3f582c9773))

### [1.11.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.11.0...1.11.1) (2023-03-03)


### Features

* add connection mode to AM ([#422](https://github.com/rudderlabs/rudder-config-schema/issues/422)) ([dabe652](https://github.com/rudderlabs/rudder-config-schema/commit/dabe65217c67b971ecb496d9340e3c4b190a4f3b))

## [1.11.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.10.0...1.11.0) (2023-03-02)

## [1.10.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.9.0...1.10.0) (2023-02-28)


### Features

* add beta to courier destination ([#409](https://github.com/rudderlabs/rudder-config-schema/issues/409)) ([93fe0ed](https://github.com/rudderlabs/rudder-config-schema/commit/93fe0edae50f1f71e15d8cb40ef55ce31dd246c2))
* upgrade ga version to 5.1.0 ([#354](https://github.com/rudderlabs/rudder-config-schema/issues/354)) ([29c5d11](https://github.com/rudderlabs/rudder-config-schema/commit/29c5d11f6994657412b2a6a779d44f79a889a8f4))

## [1.9.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.8.2...1.9.0) (2023-02-27)


### Features

* added roles for snoflake ([78f6e0d](https://github.com/rudderlabs/rudder-config-schema/commit/78f6e0d01df7ac544722e65dd548879615616ca3))

### [1.8.2](https://github.com/rudderlabs/rudder-config-schema/compare/1.8.1...1.8.2) (2023-02-27)

### [1.8.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.8.0...1.8.1) (2023-02-27)


### Features

* added customerio group call support ([#382](https://github.com/rudderlabs/rudder-config-schema/issues/382)) ([19cfdb5](https://github.com/rudderlabs/rudder-config-schema/commit/19cfdb51e13cb3d462517ae22478903ed01b1ff7))
* added new destination vitally ([#406](https://github.com/rudderlabs/rudder-config-schema/issues/406)) ([7a11e32](https://github.com/rudderlabs/rudder-config-schema/commit/7a11e322308d09ac7616e9ec4d6863825fa17e7d))
* onboard destination courier ([#379](https://github.com/rudderlabs/rudder-config-schema/issues/379)) ([22d124a](https://github.com/rudderlabs/rudder-config-schema/commit/22d124a2e1110cf96d7aefe73d50a6935def1560))
* upgrade stripe version to 5.3.0 ([#399](https://github.com/rudderlabs/rudder-config-schema/issues/399)) ([659aae1](https://github.com/rudderlabs/rudder-config-schema/commit/659aae1cf17f68157ff317f12a84e7202df02f05))

## [1.8.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.7.2...1.8.0) (2023-02-21)


### Bug Fixes

* use node 16 for test coverage ([#395](https://github.com/rudderlabs/rudder-config-schema/issues/395)) ([4f447e4](https://github.com/rudderlabs/rudder-config-schema/commit/4f447e4314da94f549a834fe424727919a3290d8))

### [1.7.2](https://github.com/rudderlabs/rudder-config-schema/compare/1.7.1...1.7.2) (2023-02-17)

### [1.7.1](https://github.com/rudderlabs/rudder-config-schema/compare/1.7.0...1.7.1) (2023-02-16)


### Features

* **ga4:** add sent_to parameter ([#381](https://github.com/rudderlabs/rudder-config-schema/issues/381)) ([bb4fd20](https://github.com/rudderlabs/rudder-config-schema/commit/bb4fd20086f617bc9e270b556b1c60522d6c0afc))


### Bug Fixes

* destination transformation change from processor to router ([#347](https://github.com/rudderlabs/rudder-config-schema/issues/347)) ([3e0f05d](https://github.com/rudderlabs/rudder-config-schema/commit/3e0f05d5c7479b39a72f478aa607c098e3636c25))

## [1.7.0](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.5...1.7.0) (2023-02-14)


### Features

* for amplitude moved oneTrustCookieCategory field to sdkTemplate ([#375](https://github.com/rudderlabs/rudder-config-schema/issues/375)) ([d02f82b](https://github.com/rudderlabs/rudder-config-schema/commit/d02f82b34090b459a7ced90e9db0afda1eac8755))
* for amplitude, moved oneTrustCookieCategory field to sdkTemplate in uiConfig ([b5820aa](https://github.com/rudderlabs/rudder-config-schema/commit/b5820aaaa10ffd146ea097264bac4759c04e7732))

### [1.6.5](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.4...1.6.5) (2023-02-13)

### [1.6.4](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.3...1.6.4) (2023-02-10)


### Features

* adds singer shopify ([98d1057](https://github.com/rudderlabs/rudder-config-schema/commit/98d1057e50c0793ffd23ed7317b98ec14ef13621))
* updates mixpanel image ([d86d0c2](https://github.com/rudderlabs/rudder-config-schema/commit/d86d0c2bccc5644a0f44aab81165f6b76b7aee39))

### [1.6.3](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.2...1.6.3) (2023-02-07)

### [1.6.2](https://github.com/rudderlabs/rudder-config-schema/compare/1.6.1...1.6.2) (2023-02-07)


### Features

* added support for  both click event and dynamic remarketing events ([#309](https://github.com/rudderlabs/rudder-config-schema/issues/309)) ([2d8a2b4](https://github.com/rudderlabs/rudder-config-schema/commit/2d8a2b420fa97d76565190ebb37b7b462c9de0af))


### Bug Fixes

* **facebook_pixel:** validation inconsistency in ui and schema ([#356](https://github.com/rudderlabs/rudder-config-schema/issues/356)) ([9b4e48d](https://github.com/rudderlabs/rudder-config-schema/commit/9b4e48d2c49aae203b11fef35099b6a2998ce51b))
* update googleAds config  ([#364](https://github.com/rudderlabs/rudder-config-schema/issues/364)) ([e2abc96](https://github.com/rudderlabs/rudder-config-schema/commit/e2abc9609bd884bf6934cf12f6eade9c204cfe73))

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
