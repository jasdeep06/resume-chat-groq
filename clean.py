# {'name': 'img_p0_1', 'height': 837, 'width': 1487, 'path': 'cache\\blogposts\\Further-into-backpropagation\\parsed\\images\\abd1d523-758c-4765-845b-172ebabcd2d9-img_p0_1', 'job_id': 'abd1d523-758c-4765-845b-172ebabcd2d9', 'original_pdf_path': 'data\\blogposts\\Further-into-backpropagation.pdf', 'page_number': 1}, {'name': 'img_p5_1', 'height': 157, 'width': 307, 'path': 'cache\\blogposts\\Further-into-backpropagation\\parsed\\images\\abd1d523-758c-4765-845b-172ebabcd2d9-img_p5_1', 'job_id': 'abd1d523-758c-4765-845b-172ebabcd2d9', 'original_pdf_path': 'data\\blogposts\\Further-into-backpropagation.pdf', 'page_number': 6}, {'name': 'img_p5_1', 'height': 157, 'width': 307, 'path': 'cache\\blogposts\\Further-into-backpropagation\\parsed\\images\\abd1d523-758c-4765-845b-172ebabcd2d9-img_p5_1', 'job_id': 'abd1d523-758c-4765-845b-172ebabcd2d9', 'original_pdf_path': 'data\\blogposts\\Further-into-backpropagation.pdf', 'page_number': 6}, {'name': 'img_p5_2', 'height': 33, 'width': 268, 'path': 'cache\\blogposts\\Further-into-backpropagation\\parsed\\images\\abd1d523-758c-4765-845b-172ebabcd2d9-img_p5_2', 'job_id': 'abd1d523-758c-4765-845b-172ebabcd2d9', 'original_pdf_path': 'data\\blogposts\\Further-into-backpropagation.pdf', 'page_number': 6}, {'name': 'img_p5_3', 'height': 29, 'width': 133, 'path': 'cache\\blogposts\\Further-into-backpropagation\\parsed\\images\\abd1d523-758c-4765-845b-172ebabcd2d9-img_p5_3', 'job_id': 'abd1d523-758c-4765-845b-172ebabcd2d9', 'original_pdf_path': 'data\\blogposts\\Further-into-backpropagation.pdf', 'page_number': 6}, {'name': 'img_p5_1', 'height': 157, 'width': 307, 
# 'path': 'cache\\blogposts\\Further-into-backpropagation\\parsed\\images\\abd1d523-758c-4765-845b-172ebabcd2d9-img_p5_1', 'job_id': 'abd1d523-758c-4765-845b-172ebabcd2d9', 'original_pdf_path': 'data\\blogposts\\Further-into-backpropagation.pdf', 'page_number': 6}]
import os
import pickle
import shutil

#remove images with same name and keep only the first
def remove_duplicate_images(image_dicts):
    seen = set()
    new_image_dicts = []
    for image_dict in image_dicts:
        if image_dict['name'] not in seen:
            new_image_dicts.append(image_dict)
            seen.add(image_dict['name'])
    return new_image_dicts

def copy_file_to_target(source_path,target_path):
    if not os.path.exists(target_path):
        shutil.copyfile(source_path,target_path)
        return True
    return False
    

if __name__ == "__main__":
    # folders_of_interest = ['blogposts','experience-blogs']
    # for folder in folders_of_interest:
    #     for subfolder in os.listdir(os.path.join('cache',folder)):
    #         parse_path = os.path.join('cache',folder,subfolder,'parsed')
    #         image_dicts = pickle.load(open(os.path.join(parse_path,'images.pkl'),'rb'))
    #         new_image_dicts = remove_duplicate_images(image_dicts)
    #         with open(os.path.join(parse_path,'images.pkl'),'wb') as f:
    #             pickle.dump(new_image_dicts,f)
    #         print(f"Removed duplicates from {subfolder}")
    #copy images to dest
    dest = os.path.join('cache','all_images')
    folders_of_interest = ['blogposts','experience-blogs']
    for folder in folders_of_interest:
        for subfolder in os.listdir(os.path.join('cache',folder)):
            image_path = os.path.join('cache',folder,subfolder,'parsed','images')
            for image in os.listdir(image_path):
                source_path = os.path.join(image_path,image)
                target_path = os.path.join(dest,image + '.png')
                copy_file_to_target(source_path,target_path)
                print(f"Copying {source_path} to {target_path}")
