import { route } from "@nextgisweb/pyramid/api";
import { errorModal } from "@nextgisweb/gui/error";

export const useSource = () => {

    const ResourceFile = async (id) => {
        const resourceFile = await route("file_resource.data", id).get();
        return resourceFile;
    }

    const listFile = async () => {
        const value = await route("file_resource.all").get();
        return value;
    }

    const listResourceFile = async (id) => {
        const value = await route("file_resource.show", id).get();
        return value;
    }

    const createItem = async (id, fid) => {
        try {
            await route("file_resource.create", id, fid).get();
        }
        catch (err) {
            errorModal(err);
        }
    }
    const deleteItem = async (id, fid) => {
        try {
            await route("file_resource.delete", id, fid).get();
        }
        catch (err) {
            errorModal(err);
        }
    }

    const deleteItems = async (id) => {
        try {
            await route("file_resource.delete_all", id).get();
        }
        catch (err) {
            errorModal(err);
        }
    }


    return { createItem, listFile, listResourceFile, deleteItem, deleteItems, ResourceFile };
};
