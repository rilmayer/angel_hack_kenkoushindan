zip -r ./upload.zip *
aws lambda \
    update-function-code \
    --function-name image_to_text \
    --zip-file fileb:///Users/k_kitahara/workspace/angel_hack_kenkoushindan/cv_api/cv_api_lambda/upload.zip \
    --publish
rm -rf ./upload.zip

