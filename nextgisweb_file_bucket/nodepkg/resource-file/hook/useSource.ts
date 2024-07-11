import { route } from "@nextgisweb/pyramid/api";
import { errorModal } from "@nextgisweb/gui/error";

export const useSource = () => {

    const ListFile = async () => {
        const listFile = await route("file_resource.all").get(); // список всех файлов
        return listFile;
    }

    const ListResourceFile = async (id) => {
        const listResource = await route("file_resource.show", id).get(); // список файлов ресурса
        return listResource;
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


    return { ListFile, ListResourceFile, createItem, deleteItem, deleteItems };
};
